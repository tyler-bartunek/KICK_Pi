import pigpio
from ShiftRegister import *

class SPIHub:
	
	def __init__(self, pi, register:ShiftRegister):

		self.pi = pi
		self.reg = register

		self.h_spi = None
		
		pass

	def enable_bus(self, channel, rate) -> None:

		if not self.h_spi:
			#Last zero is for flags
			self.h_spi = self.pi.spi_open(channel, rate, 0)

	def disable_bus(self) -> None:

		if self.h_spi:
			self.pi.spi_close(self.h_spi)
		
		self.h_spi = None

	def toggle_cs(self, line_id:str) -> None:

		line_dict = {'RL':0b01111111, 'CL':0b10111111, 'FL':0b11011111,
		             'FR':0b11101111, 'CR':0b11110111, 'RR':0b11111011,
					 'XX':0b11111111}

		self.reg.write(line_dict[line_id])


	def transfer(self, line_id:str, data:int, channel, rate):

		#Tentative plan: open bus if not open, select line, send message, line high

		#Select line
		self.toggle_cs(line_id)

		#Enable the bus if it isn't already active
		self.enable_bus(channel, rate)

		(count, rx) = pi.spi_xfer(self.h_spi, data)

		return rx
