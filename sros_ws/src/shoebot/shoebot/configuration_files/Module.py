
from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist

#Base module, defines common behavior for all modules.
#Overwritten within inherited classes
class Module(ABC):

    def __init__(self, node, active_paths, device_ids):

        pass

    @abstractmethod
    def fetch_commands(self, vel_cmd: Twist, feedback) -> list:

        pass
    
    @abstractmethod
    def compute_received(self, active_paths, device_ids, device_data) -> dict[str, dict[str, float]]:

        pass

