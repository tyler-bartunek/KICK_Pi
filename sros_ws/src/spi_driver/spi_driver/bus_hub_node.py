
#Import client library
import rclpy
from rclpy.node import Node

#Import dependencies from hardware_interfaces
from hardware_interfaces import DeviceInterface, Harness

from spi_driver.msg import SPIFrame, DeviceData

class BusManager():

    def __init__(self, node):

        self.num_paths = 6
        self.comms_rate = 5e6
        self.spi = Harness()
        self.channel = 0
        self.devices = {path_id:DeviceInterface(self, node, path_id, self.channel) for path_id in range(self.num_paths)}

    def who_are_you_handshake(self, path_id):

        #Configure the SPI Bus to default settings for discovery
        discovery_rate = 32000

        #Perform the handshake
        path_header = 0xF | (path_id & 0x7) #First four bits are 1111, rest are path_id
        handshake_data = [path_header, 0xFF, 0x00, 0x00]
        checksum = self.compute_checksum(handshake_data)
        handshake_message = handshake_data + [checksum, 0xCF] #add checksum and padding that prevents bit-stuffing
        response = self.spi.transfer(path_id, handshake_message, self.channel, discovery_rate) #Send handshake_message and get response

        #Disable the bus, freeing it for other activities
        self.spi.disable_bus()

        #Expected it to return padding, path_header, the device_id, data, and then the checksum
        expected = [0xCF, path_header, 0x00, 0x00, 0x00, checksum]
        if response[5] == expected[5]:
            return response[2] #Returns the identifier for the module
        else:
            return None #No device on this path

    def discover_device(self, device):

        if device.status == "inactive":
            device_id = self.who_are_you_handshake(path_id)

            if device_id:
                self.node.get_logger().info(f"Device discovered on path {device.path_id} with ID {device_id}")
                device.status = "active"
                device.id = device_id
                device.comms_rate = self.comms_rate

    def detect_fault(self, cmd_data:list, response_data:list, device):
        #Extract path_id from cmd_data
        path_id = cmd_data[0] & 0x7

        #If the checksum fails, this could indicate a fault in the communication or the device. If the checksum is correct but the path_id or device_id doesn't match, this could indicate a mismatch in the expected response, which may also suggest a fault.
        if response_data[5] != self.compute_checksum(cmd_data[:-1]):
            self.node.get_logger().warn(f"Checksum failure detected in response: {response_data}")
            #If the checksum is 0xFF but this is not expected for the response values, internal fault on device may be indicated
            if self.compute_checksum(response_data[1:-2]) == 0xFF:
                self.node.get_logger().warn(f"Device on path {path_id} may be experiencing internal fault")
                device.status = "fault" #known fault state
            return True

        #If the checksum is correct but the path_id or device_id doesn't match, this could indicate a mismatch in the expected response, which may also suggest a fault.
        elif response_data[1] != cmd_data[0]:
            self.node.get_logger().warn(f"Path ID mismatch in response on path: {response_data, path_id}")
            return True
        elif response_data[2] != device.id:
            self.node.get_logger().warn(f"Device ID mismatch in response on path: {response_data, path_id}")
            return True
        #If we pass these checks, the data is likely good.
        else:
            device.status = "active"
            return False

    def compute_checksum(self, data:list):
        
        return sum(data) % 256

    def poll_devices(self, cmd):

        for path_id, device in self.devices.items():   
            if device.status != device.prev_status:
                if device.status == "active":
                    device.activate()
                else:
                    if device.status == "fault":
                        self.node.get_logger.info(f"Deactivating device on path {path_id}")
                    device.deactivate()
            else:
                if device.status == "active":
                    response = self.spi.transfer(path_id, cmd, device.channel, device.comms_rate)
                    #TODO: Package response into SPIFrame message
                    if self.detect_fault(cmd, response, device):
                        device.status = "fault"
                        self.node.get_logger().info(f"Fault detected on path {path_id}")
                    else:
                        device.publisher.publish(response)
                else:
                    if device.status == "inactive":
                        self.discover_device(device)
                pass

class BusHubNode(Node):

    def __init__(self):
        super().__init__("bus_hub")

        #Create the BusManager object, fetch the initial state of the bus
        self.bus = BusManager(self)
        for path_id, device in self.bus.devices.items():
            self.bus.discover_device(device)

        #Create a timer and timer callback that polls each device periodically
        timer_period = 0.001 # seconds
        self.timer = self.create_timer(timer_period, self.bus.poll_devices)

        #Create a subscriber that listens for commands from the ShoeBot node
        self.subscriber = self.create_subscription(cmdFrame, "shoebot/cmd", self.cmd_callback, 10)

    
    def cmd_callback(self, msg):
        # Handle the incoming command message

        raise NotImplementedError


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