
#Basic ROS functionality
import rclpy
from rclpy.node import Node

#Topic message formats
from shoebot_interfaces.msg import BatteryInfo, cmdFrame
from std_msgs.msg import String, geometry_msgs.msg.Twist

#Service message formats
from shoebot_interfaces.srv import ConfigUpdate

#Configuration files for different kinematic configurations
from .configuration_files import Echo, Wheels

class ShoeBotNode(Node):

    def __init__(self):
        super().__init__('shoebot_node')

        #ShoeBot parameters
        self.battery_threshold = 3.1 #Voltage threshold for low battery warning, in volts
        self.kinematic_config = 'Echo'

        #Create the subscriber to the battery monitoring topic
        self.battery_subscriber = self.create_subscription(BatteryInfo, 'battery-info', self.battery_callback, 10)

        #Create the subscriber to the motion_plan topic, notably velocity commands
        self.vel_subscriber = self.create_subscription(geometry_msgs.msg.Twist, 'shoebot/cmd_vel', self.vel_callback, 10)

        #Create service server for configuration updates
        self.config_server = self.create_service(ConfigUpdate, 'shoebot/config_update', self.config_update_callback)

        #Create publisher for actuator command topic
        self.actuator_cmd_publisher = self.create_publisher(ActuatorCmdFrame,'shoebot/cmd', 10)


    def battery_callback(self, msg):
        #TODO: Handle incoming battery status message, and decide how to warn the user and when to shut it down

        pass

    def vel_callback(self, msg):
        #TODO: Handle incoming velocity command, and decide how to send it to the motor controller

        pass

    def config_update_callback(self, response):
        #TODO: Handle incoming configuration update request, and decide how to update the kinematic configuration and respond to the service call
        pass


def main(args = None):

    rclpy.init(args = args)

    shoebot_node = ShoeBotNode()

    rclpy.spin(shoebot_node)

    shoebot_node.destroy_node()
    rclpy.shutdown()