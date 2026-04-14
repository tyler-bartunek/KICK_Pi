from .Module import Module

from geometry_msgs.msg import Twist
import numpy as np

class Wheels(Module):

    X_CONFIG = [0x01, 0x02, 0x01, 0x02]
    O_CONFIG = [0x02, 0x01, 0x02, 0x01]

    def __init__(self, node, active_paths, device_ids):
        super().__init__()

        self.node = node
        self.jacobian = None
        self.detect_configuration(active_paths, device_ids)

    def detect_configuration(self, active_paths, device_ids):

        #Compare the device_ids at indices where active_paths is true to known configurations
        devices = [device for device, active in zip(device_ids, active_paths) if active]

        if devices == self.X_CONFIG:
            self.jacobian = self.X_Jacobian()
        elif devices == self.O_CONFIG:
            self.jacobian = self.O_Jacobian()
        else:
            self.node.get_logger().warn(f"Unrecognized wheel configuration: {devices}, unable to set Jacobian")

    def fetch_commands(self, vel_cmd: Twist, feedback) -> list:

        #TODO: Convert vel_cmd into a 4x1 velocity vector, then compute the required wheel speeds using the Jacobian
        #and control law

        pass

    def compute_received(self, active_paths, device_ids, device_data) -> dict[str, dict[str, float]]:

        #TODO: Invert Jacobian with safeguards, take command data and reconstruct center of mass velocity

        pass

    def X_Jacobian(self):
        raise NotImplementedError

    def O_Jacobian(self):
        raise NotImplementedError
