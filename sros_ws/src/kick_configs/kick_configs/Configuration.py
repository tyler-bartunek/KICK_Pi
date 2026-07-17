
from abc import ABC, abstractmethod
from geometry_msgs.msg import Twist

#Base configuration class, defines common behavior for all configuration files.
#Overwritten within inherited classes
class Configuration(ABC):

    def __init__(self, node, active_paths, device_ids):

        self.node = node
        self.active_paths = active_paths
        self.device_ids = device_ids
        
        rail_sep = self.node.get_parameter('rail-spacing')._value
        self.module_locations = self.node.get_parameter('module-placement')._value
        
        #Hard-code segment length for now, fix later
        seg_length = 64.0 #mm, average
        
        x_coord = (0.5 * rail_sep) + 56.2 # Far-edge of the trapezoidal point of rail, makes measuring offset easier
        
        #Relative to presumed center of robot
        self.LOCATION_BASE_COORDS = {0:(-x_coord, -seg_length * 2), 
                                     1:(-x_coord, 0), 
                                     2:(-x_coord, seg_length * 2), 
                                     3:(x_coord, seg_length * 2), 
                                     4:(x_coord, 0), 
                                     5:(x_coord, -seg_length * 2)}
        
        self.module_coords = self.compute_module_coords()

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

    def compute_module_coords(self):
        
        #Hard-coded constant for now
        ridge_distance = 7.8 #mm, average
        
        actual_locations = self.LOCATION_BASE_COORDS.copy()
        
        for loc, position_adj in enumerate(self.module_locations):
            
            actual_locations[loc][1] += self.position_adj * ridge_distance
        
        return actual_locations
