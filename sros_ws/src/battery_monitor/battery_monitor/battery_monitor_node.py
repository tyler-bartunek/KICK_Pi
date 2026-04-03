
#TODO: Import ADS monitoring library

#ROS stuff
import rclpy
from rclpy.node import Node

#TODO: Import relevant message type for battery-info topic

class BatteryMonitor(Node):

    def __init__(self):
        super().__init__('battery-monitor')
        #TODO: Create publisher to battery-info topic, decide on message format
        #self.publisher_ = self.create_publisher(<insert type>, 'battery-info', 10)
        raise NotImplementedError

    def timer_callback(self):

        raise NotImplementedError


def main():

    rclpy.init(args = args)

    battery_status_checker = BatteryMonitor()

    rclpy.spin(battery_status_checker)

    battery_status_checker.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()