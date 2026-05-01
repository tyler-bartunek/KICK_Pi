
from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist

#Base configuration class, defines common behavior for all configuration files.
#Overwritten within inherited classes
class Configuration(ABC):

    def __init__(self, node, active_paths, device_ids):

        self.node = node
        self.active_paths = active_paths
        self.device_ids = device_ids

        pass

    @abstractmethod
    def fetch_commands(self, vel_cmd: Twist, feedback) -> list:

        pass
    
    @abstractmethod
    def compute_received(self, device_data) -> Twist:

        pass

    def dict_to_twist(self, dictionary: dict[str, dict[str, float]]) -> Twist:

        msg = Twist()
        msg.linear.x = dictionary['linear']['x']
        msg.linear.y = dictionary['linear']['y']
        msg.linear.z = dictionary['linear']['z']
        msg.angular.x = dictionary['angular']['x']
        msg.angular.y = dictionary['angular']['y']
        msg.angular.z = dictionary['angular']['z']

        return msg

