
import rclpy
from rclpy.node import Node


class ShoeBotNode(Node):

    def __init__(self):
        super().__init__('shoebot_node')
        self.battery_subscriber = self.create_subscription(battery_info, 'battery-info', self.battery_callback, 10)


    def battery_callback(self, msg):
        #TODO: Handle incoming battery status message, and decide how to warn the user and when to shut it down

        pass


def main(args = None):

    rclpy.init(args = args)

    shoebot_node = ShoeBotNode()

    rclpy.spin(shoebot_node)

    shoebot_node.destroy_node()
    rclpy.shutdown()