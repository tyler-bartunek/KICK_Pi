
#Base module, defines common behavior for all modules.
#Overwritten within inherited classes
class Module:

    def __init__(self):

        raise NotImplementedError

    def get_commands_from_vel(self, vel_cmd):

        pass

    def get_vel_from_commands(self, commands:list):

        pass

