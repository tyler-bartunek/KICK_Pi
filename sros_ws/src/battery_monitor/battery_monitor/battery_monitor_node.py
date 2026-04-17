
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
        #Create publisher to battery-info topic, decide on message format
        self.publisher_ = self.create_publisher(BatteryInfo, 'battery-info', 10)
        
        #ADS stuff
        bus_number = 1 #hardcoded for now
        self.ads = self.connect_ads(bus_number)
        self.pin_to_read = 0
        timer_freq = 10.0 #Hz
        timer_period = 1.0 / timer_freq
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):

        self.ads.requestADC(self.pin_to_read)
        value = self.ads.getValue()

        #TODO: Convert value to voltage and package into message, publish to topic
        voltage = self.ads.toVoltage(value)
        msg = battery_info()
        msg.voltage = voltage
        self.publisher_.publish(msg)
        
    #Configure and set the ADS object: Hardcoded for now, might change later
    def connect_ads(i2cbus_number):

        #Set it up at the default address and specified bus number 
        ads = ADS1x15.ADS1115(i2cbus_number)

        #Set the gain to accept up to $\pm$ 4.096V and have acceptable resolution
        ads.setGain(ads.PGA_4_096V)

        #Set the mode: CONTINUOUS
        ads.setMode(ads.MODE_CONTINUOUS)

        #Set the data rate: fastest
        ads.setDataRate(ads.DR_ADS111X_860)

        return ads
    

def main(args = None):

    rclpy.init(args = args)

    battery_status_checker = BatteryMonitor()

    rclpy.spin(battery_status_checker)

    battery_status_checker.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()