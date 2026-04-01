
#Import client library
import rclpy
from rclpy.node import node

#Import dependencies from hardware_interfaces
from hardware_interfaces import ShiftRegister, DeviceInterface


class BusHubNode(Node):

    def __init__(self):
        super.__init__("bus_hub")
        num_paths = 6

        self.active_paths = {}
        for path_id in range(num_paths):
            if self.who_are_you_handshake(path_id):
                # Dynamically create the publisher for THIS specific path
                topic_name = f"path_{path_id}/data"
                self.active_paths[path_id] = self.create_publisher(MySpiMsg, topic_name, 10)
                self.get_logger().info(f"Initialized Device on Path {path_id}")

    def who_are_you_handshake(self, path_id):

        raise NotImplementedError



def main():

    #Start the client library
    rclpy.init(args = args)

    bus_hub = BusHubNode()

    #TODO: Check if the spin_until_future_complete makes more sense here
    rclpy.spin(bus_hub)

    bus_hub.destroy_node()
    rclpy.shutdown()

    raise NotImplementedError


if __name__ == "__main__":
    main()