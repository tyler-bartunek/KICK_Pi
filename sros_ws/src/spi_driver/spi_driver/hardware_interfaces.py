

import RPi.GPIO
import spidev


class ShiftRegister:

    def __init__(self):

        raise NotImplementedError


class DeviceInterface:

    def __init__(self, node, path_id):
        self.path_id = path_id
        # The peripheral "talks" to the world here
        self.pub = node.create_publisher(DataMsg, f"path_{path_id}/data", 10)
        # The world "talks" to the peripheral here
        self.sub = node.create_subscription(CmdMsg, f"path_{path_id}/cmd", self.cmd_callback, 10)
        self.last_cmd = None

    def cmd_callback(self, msg):
        self.last_cmd = msg # Queue this up for the next SPI cycle
