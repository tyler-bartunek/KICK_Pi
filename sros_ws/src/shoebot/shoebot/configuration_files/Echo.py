
from .Module import Module
from geometry_msgs.msg import Twist

class Echo(Module):

    def __init__(self, node, active_paths, device_ids):
        super().__init__()

    def fetch_commands(self, vel_cmd: Twist, feedback:list) -> list:
        #Package the magnitudes of linear and angular vels as a pair of bytes, sends to all nodes
        linear_vel = int(self.compute_amplitude(vel_cmd.linear.x, vel_cmd.linear.y, vel_cmd.linear.z))
        angular_vel = int(self.compute_amplitude(vel_cmd.angular.x, vel_cmd.angular.y, vel_cmd.angular.z))

        return [linear_vel, angular_vel] * 6

    def compute_received(self, active_paths, device_ids, device_data):

        #Returns the 2-byte integer value sent to each module
        #TODO: Repackage into a format compatible with a Twist message
        return (device_data[0] << 8) | device_data[1]

    def compute_amplitude(x, y, z):

        return (x ** 2 + y ** 2 + z ** 2) ** 0.5