
#Import client library
import rclpy
from rclpy.node import Node


from bus_manager import BusManager

#Import custom interfaces
from kickbot_interfaces.msg import BusState, ActuatorCmdFrame
from kickbot_interfaces.srv import ConfigUpdate


class BusHubNode(Node):

    def __init__(self):
        super().__init__("bus_hub")

        #Create the BusManager object, fetch the initial state of the bus
        self.bus = BusManager(self)
        for path_id, device in self.bus.devices.items():
            self.bus.discover_device(device)

        self.config_client = self.create_client(ConfigUpdate, "kickbot/config_update")

        #Create a timer and timer callback that polls each device periodically
        self.bus_publisher = self.create_publisher(BusState, "kickbot/bus_state", 10)
        timer_freq = 500. #Hz
        timer_period = 1. / timer_freq # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        #Create a subscriber that listens for commands from the KickBot node
        self.cmd_subscriber = self.create_subscription(ActuatorCmdFrame, "kickbot/cmd", self.cmd_callback, 10)

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

    #Release the chip and request objects, as well as the spi kernel
    bus_hub.bus.reg.cleanup()
    bus_hub.bus.spi.disable_bus()
    #Shutdown ROS stuff
    bus_hub.destroy_node()
    rclpy.shutdown()



if __name__ == "__main__":
    main()