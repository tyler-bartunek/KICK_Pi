#Basic functionality
import spidev
import random #Specifically for the false board tests

#Custom tools
from ShiftRegister import *
from BOARD_GLOBALS import *

class SPIHub:
	
	def __init__(self, register:ShiftRegister):

		self.reg = register

		#Initialize spi as None so enable bus logic works
		self.spi = None
		

	def enable_bus(self, channel, rate) -> None:

		if not self.spi:
			#Create and configure the spi object
			self.spi = spidev.SpiDev()
			self.spi.open(channel, 0) #Bus 0, Device (CE line) 0
			#Set the rate, and mode to be mode 0
			self.spi.max_speed_hz = rate
			self.spi.mode = 0


	def disable_bus(self) -> None:

		if self.spi:
			self.spi.close()
		
		self.spi = None


	def toggle_cs(self, line_id:str, testing:bool = False, default_cs = CS) -> None:

		#Logic to select line based on line_id, with cases 8 and 9 encapsulating 
		#select none and select default cs line, respectively
		line_dict = {0:0b01111111, 1:0b10111111, 2:0b11011111,
		             3:0b11101111, 4:0b11110111, 5:0b11111011,
					 8:0xFF, 9:0xFF}
		alt_keys_numeric = list(range(7))
		
		#need to add logic to check if alternate keys are being used
		line_to_select = line_dict[line_id]

		if testing and (line_id == 9):
			GPIO.output(default_cs, 0)
		else:
			self.reg.write(line_to_select)


	def transfer(self, line_id:str, data:int, channel, rate, testing:bool = False, default_cs = CS):

		#open bus if not open, select line, send message, line high

		#Select line
		self.toggle_cs(line_id, testing = testing, default_cs = default_cs)

		#Enable the bus if it isn't already active
		self.enable_bus(channel, rate)

		rx = self.spi.xfer(data)

		#Pulse CS high at end of transaction
		self.toggle_cs(8, default_cs = default_cs)

		return rx

#False Board for Simulation/Debugging Purposes
class FalseBoard(SPIHub):

	def __init__(self, register:ShiftRegister):
		
		self.reg = register

		#Define spi handle as None so enable_bus and disable_bus logic works correctly
		self.spi = None

	def transfer(self, line_id:str, data:bytes, channel, rate):

		#Added this to make sure that the sync-up works for peripheral detection
		if data == b'\xFF':
			return data
		else:
			return random.randint(0,255)