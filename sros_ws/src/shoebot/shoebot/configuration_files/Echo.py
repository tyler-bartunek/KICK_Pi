
from .Module import Module

class Echo(Module):

    def __init__(self):
        super().__init__()
        raise NotImplementedError

    def get_commands_from_vel(self, vel_cmd):
        #Doesn't actually compute anything, packages the vel_cmd as a pair of bytes, sends to all active paths

        pass

    def get_vel_from_commands(self, commands:list):

        #Returns the 2-byte integer value sent to each module
        return (commands[0] << 8) | commands[1]