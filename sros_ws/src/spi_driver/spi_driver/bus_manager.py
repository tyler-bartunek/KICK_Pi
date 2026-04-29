#Import client library
import rclpy
from rclpy.node import Node

#Import custom interfaces
from kickbot_interfaces.msg import BusState, ActuatorCmdFrame

#Import dependencies from hardware_interfaces
from hardware_interfaces import DeviceInterface, Harness

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

        #Perform the handshake, attempt it 10 times
        handshake_message = self.frame_message(path_id, 0x00, [0x00, 0x00]) #Device ID is 0 for handshake, data is just padding
        response = [0x00] * 6
        attempts = 0
        while (response[0] & 0x7) != path_id:
            try:
                response = self.spi.transfer(path_id, handshake_message, self.channel, discovery_rate)
            except Exception as e:
                self.node.get_logger().error(f"SPI transfer failed on path {path_id}: {e}")
                return None

            attempts += 1

            if attempts > 9:
                return None #No device on this path

        #Disable the bus, freeing it for other activities
        self.spi.disable_bus()

        return response[1] #Returns the identifier for the module if successful
    
    
    def frame_message(self, path_id, device_id, data:list):
        path_header = 0xF | (path_id & 0x7) #First four bits are 1111, rest are path_id
        message_data = [0xBF,path_header, device_id] + data + [self.compute_checksum([path_header, device_id] + data)]

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
        path_id = cmd_data[1] & 0x7

        #If the checksum fails, this could indicate a fault in the communication or the device. If the checksum is correct but the path_id or device_id doesn't match, this could indicate a mismatch in the expected response, which may also suggest a fault.
        if response_data[4] != self.compute_checksum(response_data[0:-2]):
            self.node.get_logger().warn(f"Checksum failure detected in response: {response_data}")
            
            #If the checksum is 0xFF but this is not expected for the response values, internal fault on device may be indicated
            if (response_data[4] == 0xFF):
                self.node.get_logger().warn(f"Device on path {path_id} may be experiencing internal fault")
            
            self.check_fault_threshold(device)
            return True

        #If the checksum is correct but the path_id or device_id doesn't match, this could indicate a mismatch in the expected response, which may also suggest a fault.
        elif response_data[0] != cmd_data[1]:
            self.check_fault_threshold(device)
            self.node.get_logger().warn(f"Path ID mismatch in response on path: {response_data, path_id}")
            return True
        elif response_data[1] != device.id:
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
        msg.active_paths = [False] * self.num_paths
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
                    response = [path_id] + [0x00] * 3 + [0xFF, 0xBF] #Default response in case of failure, with recognizable invalid checksum and path_id for debugging
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
                        msg.active_paths[path_id] = True
                        msg.device_ids[path_id] = device.id
                        msg.device_data[path_id*2:path_id*2+2] = response[3:5] #Assuming data is always 2 bytes, and in these positions, may need to be updated based on actual response format
                else:
                    if device.status == "inactive":
                        self.discover_device(device)
        #Publish the bus state message after polling all devices
        self.node.bus_publisher.publish(msg)