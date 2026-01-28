import pigpio
import struct

class Module():

    def __init__(self, pi, identifier):

        self.status = 'DISCONNECTED'
        self.identifier = identifier
        self.h_spi = None

    def enable_bus(self, channel, rate) -> None:

		if not self.h_spi:
			#Last zero is for flags
			self.h_spi = self.pi.spi_open(channel, int(rate), 0)


	def disable_bus(self) -> None:

		if self.h_spi:
			self.pi.spi_close(self.h_spi)
		
		self.h_spi = None

    def Transfer(self, data):

        StateMachineOpts = {'DISCONNECTED':self.OnDisconnected(data), 'TRANSMITTING':self.OnTransmit(data), 'SUSPECT':self.OnSuspect(data)}

        StateMachineOpts[self.status]

    def OnDisconnected(self, data):

        sending = [b'\xFF', b'\xAA', b'\x55', b'\xFF']

        #TODO: Add SPI stuff

        raise NotImplementedError

    def OnTransmit(self, data):

        sending = self.FrameMessage(data)
        #TODO: Add SPI stuff

        raise NotImplementedError

    def OnSuspect(self, data):

        raise NotImplementedError

    def FrameMessage(self, data):

        data_to_send = struct.pack('>h', data)

        crc = self.CRC_Generator(data)

        return [self.identifier] + list(data_to_send) + [crc]

    def ParseMessage(self, message):

        buffer = bytearray(message)
        header, data, crc = struct.unpack('>BhB', buffer)

        valid_CRC = self.CRC_Checker(data, crc)
        valid_header = self.Checksum(header)

        if valid_header and valid_CRC:
            self.status = 'TRANSMITTING'
            return data
        else:
            self.status = 'SUSPECT'

    def CRC_Checker(self, message, crc) -> bool:

        return self.CRC_Generator(message) == crc

    def CRC_Generator(self, data):

        raise NotImplementedError

    def Checksum(self, header):

        raise NotImplementedError


class EchoDevice(Module):

    def __init__(self, pi):

        ID = b'\xF0'

    def run(self, data):

        raise NotImplementedError
        
    def EchoLeader(self, data):

        self.Transfer(data)

