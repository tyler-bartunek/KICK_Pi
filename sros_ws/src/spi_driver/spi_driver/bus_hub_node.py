
#Import client library
import rclpy
from rclpy.node import Node

#Import dependencies from hardware_interfaces
from hardware_interfaces import DeviceInterface, Harness

#Import custome interfaces
from shoebot_interfaces.msg import BusState, ActuatorCmdFrame
from shoebot_interfaces.srv import ConfigUpdate

class BusManager():

    def __init__(self, node):

        self.num_paths = 6
        self.comms_rate = 5e6
        self.spi = Harness()
        self.channel = 0
        self.node = node
        self.devices = {path_id:DeviceInterface(path_id, self.channel) for path_id in range(self.num_paths)}
        self.device_ids = [None] * self.num_paths
        self.active_paths = [False] * self.num_paths
        self.prev_active_paths = self.active_paths.copy()

    def who_are_you_handshake(self, path_id):

        #Configure the SPI Bus to default settings for discovery
        discovery_rate = 32000

        #Perform the handshake
        handshake_message = self.frame_message(path_id, 0x00, [0x00, 0x00]) #Device ID is 0 for handshake, data is just padding
        response = []
        try:
            response = self.spi.transfer(path_id, handshake_message, self.channel, discovery_rate)
        except Exception as e:
            self.node.get_logger().error(f"SPI transfer failed on path {path_id}: {e}")
            return None

        #Disable the bus, freeing it for other activities
        self.spi.disable_bus()

        #Expected it to return padding, path_header (index 0 of handshake), the device_id, data (2 bytes), and then the checksum
        checksum = self.compute_checksum(handshake_message[:-1]) #Checksum is computed on all bytes except the checksum itself
        if response[5] == checksum:
            return response[2] #Returns the identifier for the module
        else:
            return None #No device on this path
    
    def frame_message(self, path_id, device_id, data:list):
        path_header = 0xF | (path_id & 0x7) #First four bits are 1111, rest are path_id
        message_data = [path_header, device_id] + data + [self.compute_checksum([path_header, device_id] + data), 0xCF]

        return message_data

    def discover_device(self, device):

        if device.status == "inactive":
            device_id = self.who_are_you_handshake(device.path_id)

            if device_id:
                self.node.get_logger().info(f"Device discovered on path {device.path_id} with ID {device_id}")
                device.status = "active"
                self.active_paths[device.path_id] = True
                self.device_ids[device.path_id] = device_id
                device.id = device_id
                device.comms_rate = self.comms_rate

    def detect_fault(self, cmd_data:list, response_data:list, device):
        #Extract path_id from cmd_data
        path_id = cmd_data[0] & 0x7

        #If the checksum fails, this could indicate a fault in the communication or the device. If the checksum is correct but the path_id or device_id doesn't match, this could indicate a mismatch in the expected response, which may also suggest a fault.
        if response_data[5] != self.compute_checksum(response_data[1:-1]):
            self.node.get_logger().warn(f"Checksum failure detected in response: {response_data}")
            
            #If the checksum is 0xFF but this is not expected for the response values, internal fault on device may be indicated
            if (response_data[-1] == 0xFF) and (self.compute_checksum(response_data[1:-1]) != 0xFF):
                self.node.get_logger().warn(f"Device on path {path_id} may be experiencing internal fault")
            
            self.check_fault_threshold(device)
            return True

        #If the checksum is correct but the path_id or device_id doesn't match, this could indicate a mismatch in the expected response, which may also suggest a fault.
        elif response_data[1] != cmd_data[0]:
            self.check_fault_threshold(device)
            self.node.get_logger().warn(f"Path ID mismatch in response on path: {response_data, path_id}")
            return True
        elif response_data[2] != device.id:
            self.check_fault_threshold(device)
            self.node.get_logger().warn(f"Device ID mismatch in response on path: {response_data, path_id}")
            return True
        #If we pass these checks, the data is likely good.
        else:
            device.status = "active"
            return False

    def check_fault_threshold(self, device):
        device.num_faults += 1
        device.status = "fault"
        if device.num_faults >= 10:
            self.node.get_logger().warn(f"Device on path {device.path_id} has exceeded fault threshold, marking as inactive")
            device.status = "inactive"
            device.num_faults = 0

    def compute_checksum(self, data:list):
        
        return sum(data) % 256

    def poll_devices(self):

        msg = BusState()
        msg.path_active = [False] * self.num_paths
        msg.device_ids = [0] * self.num_paths
        msg.device_data = [0] * (self.num_paths * 2)
        #Update the previous active device list
        self.prev_active_paths = self.active_paths.copy()

        for path_id, device in self.devices.items():   
            if device.status != device.prev_status:
                self.node.get_logger().info(f"Status change detected on path {path_id}: {device.prev_status} -> {device.status}")
                device.prev_status = device.status

            else:
                if device.status == "active":
                    sent_packet = self.frame_message(path_id, device.id, device.cmd)
                    response = [0xCF, path_id] + [0x00] * 3 + [0xFF] #Default response in case of failure, with recognizable invalid checksum and path_id for debugging
                    try:
                        response = self.spi.transfer(path_id, sent_packet, device.channel, device.comms_rate)
                    except Exception as e:
                        self.node.get_logger().error(f"SPI transfer failed on path {path_id}: {e}")
                        self.check_fault_threshold(device)
                        continue

                    #Populate msg with data from response if no faults.
                    if self.detect_fault(sent_packet, response, device):
                        self.active_paths[path_id] = False
                        self.node.get_logger().warn(f"Fault detected on path {path_id}")
                    else:
                        self.active_paths[path_id] = True
                        msg.path_active[path_id] = True
                        msg.device_ids[path_id] = device.id
                        msg.device_data[path_id*2:path_id*2+2] = response[3:5] #Assuming data is always 2 bytes, and in these positions, may need to be updated based on actual response format
                else:
                    if device.status == "inactive":
                        self.discover_device(device)
        #Publish the bus state message after polling all devices
        self.node.bus_publisher.publish(msg)


class BusHubNode(Node):

    def __init__(self):
        super().__init__("bus_hub")

        #Create the BusManager object, fetch the initial state of the bus
        self.bus = BusManager(self)
        for path_id, device in self.bus.devices.items():
            self.bus.discover_device(device)

        self.config_client = self.create_client(ConfigUpdate, "shoebot/config_update")

        #Create a timer and timer callback that polls each device periodically
        self.bus_publisher = self.create_publisher(BusState, "shoebot/bus_state", 10)
        timer_freq = 1000. #Hz
        timer_period = 1. / timer_freq # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        #Create a subscriber that listens for commands from the ShoeBot node
        self.cmd_subscriber = self.create_subscription(ActuatorCmdFrame, "shoebot/cmd", self.cmd_callback, 10)

    def timer_callback(self):
        self.bus.poll_devices()
        self.detect_config_change()
    
    def cmd_callback(self, msg):

        for path in range(self.bus.num_paths):
            #Extract the command data for this path from the message, and update the bus manager's cmd attribute
            cmd_data = msg.cmd_data[path*2:path*2+2] #Assuming each path has 2 bytes of command data, may need to be updated based on actual message format
            self.bus.devices[path].cmd = cmd_data

    def detect_config_change(self):

        if self.bus.active_paths != self.bus.prev_active_paths:
            request = ConfigUpdate.Request()
            request.active_paths = self.bus.active_paths
            request.device_ids = self.bus.device_ids
            future = self.config_client.call_async(request)
            future.add_done_callback(self.config_update_callback)

    def config_update_callback(self, future):
        try:
            result = future.result()
            self.get_logger().info(f"Config update response: {result.config_name}")
        except Exception as e:
            self.get_logger().error(f"Config update service call failed: {e}")




def main(args = None):

    #Start the client library
    rclpy.init(args = args)

    bus_hub = BusHubNode()

    #TODO: Check if the spin_until_future_complete makes more sense here
    rclpy.spin(bus_hub)

    bus_hub.bus.spi.disable_bus()
    bus_hub.destroy_node()
    rclpy.shutdown()



if __name__ == "__main__":
    main()