from .Module import Module

class Wheels(Module):

    def __init__(self):
        super().__init__()

        raise NotImplementedError

    def get_commands_from_vel(self, vel_cmd):

        pass

    def get_vel_from_commands(self, commands:list):

        pass

    def X_Jacobian(self):
        raise NotImplementedError

    def O_Jacobian(self):
        raise NotImplementedError
