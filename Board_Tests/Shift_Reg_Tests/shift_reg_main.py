#Imports

#From adjacent files
from SHIFT_GLOBALS import *
from ShiftRegister import *

def main():
    
    #Initialize the ShiftRegister object
    shift = ShiftRegister(DATA, LATCH, SPI0_SCLK, CHANNEL)
    
    data_to_write = 31 #Random number, initially
    
    shift.write(data_to_write, RATE)
    
    #TODO: Send sinusoid to test timing

if __name__ == "__main__":
    
    main()