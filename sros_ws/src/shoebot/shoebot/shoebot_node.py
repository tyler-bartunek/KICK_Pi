
#Basic ROS functionality
import rclpy
from rclpy.node import Node

#Topic message formats
from shoebot_interfaces.msg import BatteryInfo, ActuatorCmdFrame, BusState
from geometry_msgs.msg import Twist

#Service message formats
from shoebot_interfaces.srv import ConfigUpdate

#Configuration files for different kinematic configurations
from kinematic_config_setter import CONFIGURATIONS, PARTIAL_CONFIGURATIONS

class ShoeBotNode(Node):

    def __init__(self):
        super().__init__('shoebot_node')

        #ShoeBot parameters
        self.battery_threshold = 3.1 #Voltage threshold for low battery warning, in volts
        self.config = None
        self.kinematic_config = 'Echo'

        self.desired_vel = None
        self.last_feedback = None

        #Create control loop parameters
        timer_freq = 100.0  # Hz, subject to Pi 3B+ reality
        self.timer = self.create_timer(1.0 / timer_freq, self.control_loop)

        #Create the subscriber to the battery monitoring topic
        self.battery_subscriber = self.create_subscription(BatteryInfo, 'battery-info', self.battery_callback, 10)

        #Create the subscriber to the motion_plan topic, notably velocity commands
        self.vel_subscriber = self.create_subscription(Twist, 'shoebot/cmd_vel', self.vel_callback, 10)

        #Create the subscriber to the bus state topic
        self.bus_subscriber = self.create_subscription(BusState, 'shoebot/bus_state', self.bus_callback, 10)

        #Create service server for configuration updates
        self.config_server = self.create_service(ConfigUpdate, 'shoebot/config_update', self.config_update_callback)

        #Create publisher for actuator command topic
        self.actuator_cmd_publisher = self.create_publisher(ActuatorCmdFrame,'shoebot/cmd', 10)

    def config_ready(self) -> bool:
        if not self.config:
            self.get_logger().warn("No configuration loaded, waiting for ConfigUpdate service call")
            return False
        return True

    def lookup_configuration(self, active_paths, device_ids):
        
        key = frozenset(d for d in device_ids if d is not None)

        if key in CONFIGURATIONS:
            config_class = CONFIGURATIONS[key]
            self.config = config_class(self, active_paths, device_ids)
            self.kinematic_config = f"{config_class.__name__}"
            self.get_logger().info(f"Loaded configuration: {config_class.__name__}")
        elif key in PARTIAL_CONFIGURATIONS:
            self.get_logger().warn(f"Partial configuration detected: {PARTIAL_CONFIGURATIONS[key]}")
        else:
            self.get_logger().error(f"Unrecognized device configuration: {key}")

    def config_update_callback(self, call, response):

        self.lookup_configuration(call.active_paths, call.device_ids)
        response.config_name = self.kinematic_config

        return response

    def battery_callback(self, msg):
        #TODO: Handle incoming battery status message, and decide how to warn the user and when to shut it down
        if msg.voltage < self.battery_threshold:
            self.get_logger().warn(f"Battery voltage low: {msg.voltage:.2f}V")

        pass

    def vel_callback(self, msg):
        
        self.desired_vel = msg

    def bus_callback(self, msg):
        
        self.last_feedback = msg

    def control_loop(self):

        if not self.config:
            return
        if self.desired_vel is None:
            return

        commands = self.config.fetch_commands(self.desired_vel, self.last_bus_state)
        msg = ActuatorCmdFrame()
        msg.cmd_data = commands
        self.actuator_cmd_publisher.publish(msg)

        

        
            



def main(args = None):

    rclpy.init(args = args)

    shoebot_node = ShoeBotNode()

    rclpy.spin(shoebot_node)

    shoebot_node.destroy_node()
    rclpy.shutdown()