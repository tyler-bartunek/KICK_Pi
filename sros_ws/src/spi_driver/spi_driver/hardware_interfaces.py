
#TODO: Try out gpiod. This is the current implementation using RPi.GPIO, which is simpler to set up.
import gpiod
from gpiod.line import Direction, Value
import spidev


class ShiftRegister:

    def __init__(self, data_pin:int, latch_pin:int, sck_pin:int, oe_pin:int):

        #Initialize pins
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.sck_pin = sck_pin
        self.oe_pin = oe_pin

        #Configure GPIO pins
        self.chip = gpiod.Chip("/dev/gpiochip0")
        self.connect_pins()

        #Disable outputs by default until our first write
        self.request.set_value(self.oe_pin, Value.ACTIVE)


    def write(self, data:int):

        #Set data attribute for use in callback function
        self.data_list = self.to_bitarray(data)

        active_inactive_map = {0: Value.INACTIVE, 1: Value.ACTIVE}

        #Pull latch low for shift
        self.request.set_value(self.latch_pin, Value.INACTIVE)

        #Send data bit by bit to the shift register
        for bit in self.data_list:
            self.request.set_value(self.data_pin, active_inactive_map[bit])
            self.request.set_value(self.sck_pin, Value.ACTIVE)
            self.request.set_value(self.sck_pin, Value.INACTIVE)

        #Enable outputs, shift values to storage register and outputs
        self.request.set_value(self.latch_pin, Value.ACTIVE)
        self.request.set_value(self.oe_pin, Value.INACTIVE)


    def connect_pins(self) -> None:

        self.request = self.chip.request_lines(consumer = "shift_register", 
                                                config = {
                                                (self.data_pin, self.latch_pin, self.sck_pin, self.oe_pin): gpiod.LineSettings(
                                                direction=Direction.OUTPUT,
                                                output_value=Value.INACTIVE)
                                                }
                                                )

        return None   

    def cleanup(self):

        if self.request and self.chip:
            self.request.release()
            self.chip.close()  
        
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

    def __init__(self, pins:dict[str,int]):
        
        DATA = pins['data_pin']
        LATCH = pins['latch_pin']
        SCK = pins['sck_pin']
        OE = pins['oe_pin']

        self.reg = ShiftRegister(DATA, LATCH, SCK, OE)
        
        #SYNC pin, need to configure
        self.sync_pin = pins['sync_pin']
        
        self.sync_request = self.reg.chip.request_lines(
        consumer="harness_sync",
        config={
            self.sync_pin: gpiod.LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.ACTIVE  # Active high by default, sync pulse pulls low
            )
        })
        
        #Define SPI channel and CE pin
        self.channel = pins['spi_channel']
        self.ce = pins['ce_pin_option']

        #Initialize spi as None so enable bus logic works
        self.spi = None


    def enable_bus(self, rate) -> None:

        if not self.spi:
            #Create and configure the spi object
            self.spi = spidev.SpiDev()
            self.spi.open(self.channel, self.ce) #Bus 0, Device (CE line) 0
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


    def transfer(self, line_id:int, data:int, rate):

        #open bus if not open, select line, send message, line high

        #Enable the bus if it isn't already active
        self.enable_bus(rate)
        
        #Initialize output buffer
        rx = []
        for byte in list(data):
            
            #Select line
            self.toggle_cs(line_id)
            
            try:
                rx_byte = self.spi.xfer([byte])
                rx.extend(rx_byte)
            except Exception as e:
                self.disable_bus()
                raise e

            #Pulse CS high at end of transaction
            self.toggle_cs(8)

        return rx
    
    def sync_pulse(self):

        #Active low
        self.sync_request.set_value(self.sync_pin, Value.INACTIVE)
        self.sync_request.set_value(self.sync_pin, Value.ACTIVE)
        
    def cleanup(self):
        self.reg.cleanup()
        self.sync_request.release()
        self.disable_bus()


class DeviceInterface:
    """
    Holds the internal state of each connected device
    """
    def __init__(self, path_id, channel, status="inactive", id = None, comms_rate = 3200):

        self.status = status
        self.prev_status = status
        self.path_id = path_id
        self.channel = channel
        self.id = id
        self.num_faults = 0
        self.comms_rate = comms_rate
        self.cmd = [0x00, 0x00, 0x00, 0x00]


