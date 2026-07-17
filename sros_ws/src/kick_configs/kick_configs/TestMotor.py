from .Configuration import Configuration

from geometry_msgs.msg import Twist

import numpy as np

class TestMotor(Configuration):

    def __init__(self, node, active_paths, device_ids):

        #Instantiate the parent class
        super().__init__(node, active_paths, device_ids)

    #Send commands to the motor from the test script
    def fetch_commands(self, vel_cmd: Twist, feedback) -> list:  
        
        control_signal = [0] * 24  # Initialize zeros for commands (safe)
        
        vel = int(round(vel_cmd.angular.z)) # Use the angular.z component of the velocity command as the motor command, rounded to nearest int
        
        if abs(vel) > 10000:  # Cap the command value for compatibility with motor driver codebase
            vel = 10000 if vel > 0 else -10000
            
        vel_high_byte = (vel >> 8) & 0xFF
        vel_low_byte = vel & 0xFF
        
        for path_id, path in enumerate(self.active_paths):
            if path:
                control_signal[4*path_id:4*path_id+4] = [0, 0, vel_high_byte, vel_low_byte]
            
         
        return control_signal

    def compute_received(self, device_data) -> Twist:
        
        vel_array = [data for data, active in zip(device_data, self.active_paths) if active]

        # Set the dictionary to convert to twist (manual is easiest)
        # Assumption: always on level ground
        vel = (vel_array[2] << 8) | vel_array[3] #Assuming the motor speed is sent as a 2-byte int, MSB first, at indices 2 and 3 of the data array for each active path
        return_dict = {'linear':[0.0, 0.0, 0.0], 'angular':[0.0, 0.0, vel]}

        return self.dict_to_twist(return_dict)


        