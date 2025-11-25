import pigpio

class ShiftRegister:
    
    def __init__(self, data_pin:int, latch_pin:int, sck_pin:int, spi_channel:int = 0):
        
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.sck_pin = sck_pin
        self.spi_channel = spi_channel
        
        #Configure pigpio object to control gpio
        self.pi = self.connect_pigpio()
        
        self.bit_index = 0
        
        self.done_sending = False
        
        
    def write(self, data:int, clock_rate:int):
        
        #Set data attribute for use in callback function
        self.data_list = self.to_bitarray(data)
        
        #Pull latch low for shift, set done to false to guarantee
        #shift will happen
        self.pi.write(self.latch_pin, 0)
        self.done_sending = False
        
        #Set callback
        cb = self.pi.callback(self.sck_pin, pigpio.RISING_EDGE, self.rising_edge_callback)
        
        try:
            #Last 0 is for flags
            h_spi = self.pi.spi_open(self.spi_channel, clock_rate, 0)
            #Send garbage data on actual channel to trigger clock,
            #should run long enough for callback to finish executing
            while not self.done_sending:
                self.pi.spi_write(h_spi, b'x00')
        finally:
            self.pi.spi_close(h_spi)
    
    def connect_pigpio(self):
        
        pi = pigpio.pi()
        if not pi.connected:
            exit()
        
        pi.set_mode(self.data_pin, pigpio.OUTPUT)
        pi.set_mode(self.latch_pin, pigpio.OUTPUT)
        
        return pi
            
            
    def rising_edge_callback(self, gpio:int, level, tick):
        
        if (self.bit_index < len(self.data_list)):
            self.pi.write(gpio, self.data_list[self.bit_index])
            self.bit_index += 1
 
        else:
            #Reset index, pull latch high to shift to storage,
            #update done_sending flag
            self.bit_index = 0
            self.pi.write(self.latch_pin, 1)
            self.done_sending = True
            
             
    def to_bitarray(self, data:int) -> list:
        
        bit_array = []
        remainder = data
        
        for i in range(7,-1-1):
            
            current_bit = 2 ** i
            if remainder >= current_bit:
                bit_array.append(1)
                remainder -= current_bit
            else:
                bit_array.append(0)

        return bit_array