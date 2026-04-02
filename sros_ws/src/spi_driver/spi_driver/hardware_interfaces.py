

import RPi.GPIO as GPIO
import spidev

from spi_driver.msg import SPIFrame


class ShiftRegister:

    def __init__(self):
        
        #Hard-coding likely not ideal, but compromise until we know more about
        #how this plays with ROS.
        self.data_pin = 26
        self.latch_pin = 6
        self.sck_pin = 13
        self.oe_pin = 5
        
        #Configure GPIO pins
        GPIO.setmode(GPIO.BCM)
        self.connect_pins()

        #Disable outputs by default until our first write
        GPIO.output(self.oe_pin, 1)

        #index variable for data bitarray and flag to mark when message is sent
        self.bit_index = 0
        self.done_sending = False
        
        
    def write(self, data:int):
        
        #Set data attribute for use in callback function
        self.data_list = self.to_bitarray(data)
        
        #Pull latch low for shift
        GPIO.output(self.latch_pin, 0)
        
        #Send data bit by bit to the shift register
        for bit in self.data_list:
            GPIO.output(self.data_pin, bit)
            GPIO.output(self.sck_pin, 1)
            GPIO.output(self.sck_pin, 0)

        #Enable outputs, shift values to storage register and outputs
        GPIO.output(self.latch_pin, 1)
        GPIO.output(self.oe_pin, 0)

    
    def connect_pins(self) -> None:

        GPIO.setup(self.data_pin, GPIO.OUT)
        GPIO.setup(self.latch_pin, GPIO.OUT)
        GPIO.setup(self.sck_pin, GPIO.OUT)
        GPIO.setup(self.oe_pin, GPIO.OUT)

        return None     
             
    def to_bitarray(self, data:int) -> list:
        
        bit_array = []
        remainder = data
        
        for i in range(7,-1,-1):
            
            current_bit = 2 ** i
            if remainder >= current_bit:
                bit_array.append(1)
                remainder -= current_bit
            else:
                bit_array.append(0)

        return bit_array

class Harness:
	
	def __init__(self):

		self.reg = ShiftRegister()

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


	def toggle_cs(self, line_id:int) -> None:

		#Logic to select line based on line_id, with case 8 encapsulating connect to none
		line_dict = {0:0b01111111, 1:0b10111111, 2:0b11011111,
		             3:0b11101111, 4:0b11110111, 5:0b11111011,
					 8:0xFF}
		
		#need to add logic to check if alternate keys are being used
		line_to_select = line_dict[line_id]

        #Not to make this too hard-coded, but the point is to not use default CS
		self.reg.write(line_to_select)


	def transfer(self, line_id:int, data:int, channel, rate):

		#open bus if not open, select line, send message, line high

		#Select line
		self.toggle_cs(line_id)

		#Enable the bus if it isn't already active
		self.enable_bus(channel, rate)

		rx = self.spi.xfer(data)

		#Pulse CS high at end of transaction
		self.toggle_cs(8)

		return rx


class DeviceInterface:
    """
    Holds the internal state of each connected device
    """
    def __init__(self, node, path_id, channel, status="inactive", id = None):

        self.status = status
        self.prev_status = status
        self.node = node
        self.path_id = path_id
        self.channel = channel
        self.id = id

        self.publisher = None
        self.subscriber = None
    
    def activate(self):
        self.publisher = self.node.create_publisher(SPIFrame, f"path_{self.path_id}/data", 10)
        self.subscriber = self.node.create_subscription(SPIFrame, f"path_{self.path_id}/cmd", self.cmd_callback, 10)

    def deactivate(self):
        if self.publisher and self.subscriber:
            self.node.destroy_publisher(self.publisher)
            self.node.destroy_subscriber(self.subscriber)
            self.publisher = None
            self.subscriber = None


