
#TODO: Import ADS monitoring library
import ADS1x15

#ROS stuff
import rclpy
from rclpy.node import Node

#Import relevant message type for battery-info topic
from shoebot_interfaces.msg import BatteryInfo

class BatteryMonitor(Node):

    def __init__(self):
        super().__init__('battery-monitor')
        #TODO: Create publisher to battery-info topic, decide on message format
        self.publisher_ = self.create_publisher(BatteryInfo, 'battery-info', 10)
        self.pin_to_read = 0
        timer_freq = 10.0 #Hz
        timer_period = 1.0 / timer_freq
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):

        ads.requestADC(self.pin_to_read)
        value = ads.getValue()

        #TODO: Convert value to voltage and package into message, publish to topic
        voltage = ads.toVoltage(value)
        msg = battery_info()
        msg.voltage = voltage
        self.publisher_.publish(msg)

def main():

    rclpy.init(args = args)

    battery_status_checker = BatteryMonitor()

    rclpy.spin(battery_status_checker)

    battery_status_checker.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()