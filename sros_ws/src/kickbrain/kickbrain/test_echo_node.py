#Basic ROS functionality
import rclpy
from rclpy.node import Node

#Topic message formats
from kickbot_interfaces.msg import ActuatorCmdFrame, BusState
from geometry_msgs.msg import Twist

#Service message formats
from kickbot_interfaces.srv import ConfigUpdate

#Configuration files for different kinematic configurations
from kinematic_config_setter import CONFIGURATIONS, PARTIAL_CONFIGURATIONS

class TestEchoNode(Node):

    def __init__(self):
        super().__init__('test_echo_node')

        #Kick Robot parameters
        self.config = None
        self.kinematic_config = 'Echo'

        self.desired_vel = None
        self.last_feedback = None

        #Create control loop parameters
        control_timer_freq = 100.0  # Hz, subject to Pi 3B+ reality
        self.control_timer_period = 1 / control_timer_freq
        self.control_timer = self.create_timer(self.control_timer_period, self.control_loop)

        #Replace the motion_plan topic subscription with a timer callback that generates pseudo-commands
        cmd_timer_freq = 1.0  # Hz, for testing purposes
        cmd_timer_period = 1 / cmd_timer_freq
        self.cmd_timer = self.create_timer(cmd_timer_period, self.cmd_timer_callback)

        #Create the subscriber to the bus state topic
        self.bus_subscriber = self.create_subscription(BusState, 'kickbot/bus_state', self.bus_callback, 10)

        #Create service server for configuration updates
        self.config_server = self.create_service(ConfigUpdate, 'kickbot/config_update', self.config_update_callback)

        #Create publisher for actuator command topic
        self.actuator_cmd_publisher = self.create_publisher(ActuatorCmdFrame,'kickbot/cmd', 10)

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

    def cmd_timer_callback(self):
        
        #Generate a pseudo-velocity command that iterates from 0 to the max uint8_t value, then back down, to test the echo functionality
        if self.desired_vel is None:
            self.desired_vel = Twist()
            self.linear_cmd_value = 0
            self.angular_cmd_value = 0
            self.increment = 1
        else:
            #Increment command values together to maintain a consistent ratio between linear and angular components, which should be reflected in the feedback if the echo configuration is working correctly
            self.linear_cmd_value += self.increment
            self.angular_cmd_value += self.increment
            if self.linear_cmd_value > 255 or self.linear_cmd_value < 0:
                self.increment *= -1
                self.angular_cmd_value += self.increment * 2
                self.linear_cmd_value += self.increment * 2  # Reverse direction and step back within bounds
            
            #Set linear and angular components of the desired velocity message
            # to be equal-valued components that have magnitude equal to the linear_cmd_value and angular_cmd_value arguments
            self.desired_vel.linear.x = (self.linear_cmd_value / 3) ** 0.5
            self.desired_vel.linear.y = (self.linear_cmd_value / 3) ** 0.5
            self.desired_vel.linear.z = (self.linear_cmd_value / 3) ** 0.5
            self.desired_vel.angular.x = (self.angular_cmd_value / 3) ** 0.5
            self.desired_vel.angular.y = (self.angular_cmd_value / 3) ** 0.5
            self.desired_vel.angular.z = (self.angular_cmd_value / 3) ** 0.5


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

    test_echo_node = TestEchoNode()

    rclpy.spin(test_echo_node)

    test_echo_node.destroy_node()
    rclpy.shutdown()

