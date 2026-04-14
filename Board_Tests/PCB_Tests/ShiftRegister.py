import gpiod
from gpiod.line import Direction, Value

class ShiftRegister:

    def __init__(self, data_pin:int, latch_pin:int, sck_pin:int, oe_pin:int):
        
        #Hard-coding likely not ideal, but compromise until we know more about
        #how this plays with ROS.
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
                                               direction = Direction.OUTPUT,
                                               output_value = Value.INACTIVE)
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