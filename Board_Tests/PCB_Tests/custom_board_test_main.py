#Imports
import pigpio

#From adjacent files
from BOARD_GLOBALS import *
from ShiftRegister import *
from SPI_Board import *

def connect_pigpio():
        
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    return pi

def main():

    #Initialize the pigpio daemon
    pi = connect_pigpio()
    
    #Initialize the ShiftRegister object
    shift = ShiftRegister(pi, DATA, LATCH, SHIFT_CLK)
    
    #Initialize the Board class
    hub = SPIHub(pi, shift)

    try:
        shift.write(data_to_write)
    
    except KeyboardInterrupt:
        print("Process terminated by user")
        pi.spi_close(h_spi)
        #break


if __name__ == "__main__":
    
    #Execute the code
    main()
