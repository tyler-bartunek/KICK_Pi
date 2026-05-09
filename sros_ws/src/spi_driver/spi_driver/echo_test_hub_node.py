
#Import client library
import rclpy
from rclpy.node import Node


from .bus_manager import BusManager

#Import custom interfaces
from kickbot_interfaces.msg import BusState, ActuatorCmdFrame
#Service message formats
from kickbot_interfaces.srv import ConfigUpdate


class EchoTestHubNode(Node):

    def __init__(self):
        super().__init__("test_hub")

        #Create the BusManager object, fetch the initial state of the bus
        self.bus = BusManager(self)
        for path_id, device in self.bus.devices.items():
            self.bus.discover_device(device)


        #Create a timer and timer callback that polls each device periodically
        self.bus_publisher = self.create_publisher(BusState, "kickbot/bus_state", 10)
        timer_freq = 100. #Hz
        timer_period = 1. / timer_freq # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        #Create a subscriber that listens for commands from the KickBot node
        self.cmd_subscriber = self.create_subscription(ActuatorCmdFrame, "kickbot/cmd", self.cmd_callback, 10)
        
        self.config_client = self.create_client(ConfigUpdate, "kickbot/config_update")

    def timer_callback(self):
        self.detect_config_change()
        self.bus.poll_devices()
    
    def cmd_callback(self, msg):

        for path in range(self.bus.num_paths):
            #Extract the command data for this path from the message, and update the bus manager's cmd attribute
            cmd_data = msg.cmd_data[path*2:path*2+2] #Assuming each path has 2 bytes of command data, may need to be updated based on actual message format
            self.bus.devices[path].cmd = [int(cmd) for cmd in cmd_data] #Not ideal, but I can't have these np.uint8's floating around
            
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
            self.get_logger().info(f"Config update response: {result.configuration}")
        except Exception as e:
            self.get_logger().error(f"Config update service call failed: {e}")





def main(args = None):

    #Start the client library
    rclpy.init(args = args)

    echo_test_hub = EchoTestHubNode()

    #TODO: Check if the spin_until_future_complete makes more sense here
    rclpy.spin(echo_test_hub)

    #Release the chip and request objects, as well as the spi kernel
    echo_test_hub.bus.reg.cleanup()
    echo_test_hub.bus.spi.disable_bus()
    #Shutdown ROS stuff
    echo_test_hub.destroy_node()
    rclpy.shutdown()



if __name__ == "__main__":
    main()