
from .Configuration import Configuration
from geometry_msgs.msg import Twist


class Echo(Configuration):

    def __init__(self, node, active_paths, device_ids):
        super().__init__(node, active_paths, device_ids)


    def fetch_commands(self, vel_cmd:Twist, feedback:list) -> list:
        #Package the magnitudes of linear and angular vels as a pair of bytes, sends to all nodes
        linear_vel = int(self.compute_amplitude(vel_cmd.linear.x, vel_cmd.linear.y, vel_cmd.linear.z))
        angular_vel = int(self.compute_amplitude(vel_cmd.angular.x, vel_cmd.angular.y, vel_cmd.angular.z))

        return [linear_vel, angular_vel] * 6

    def compute_received(self, device_data) -> Twist:

        #2-byte int sent to each module, assumed constant MSB first
        echoed = (device_data[0] << 8) | device_data[1]
        vel_types = ['linear', 'angular']
        components = ['x', 'y', 'z']

        return_dict = {vel_type: {comp: echoed for comp in components} for vel_type in vel_types}

        return self.dict_to_twist(return_dict)

    def compute_amplitude(x, y, z):

        return (x ** 2 + y ** 2 + z ** 2) ** 0.5