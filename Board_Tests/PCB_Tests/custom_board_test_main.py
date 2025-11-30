#Imports
import pigpio
import random

#From adjacent files
from BOARD_GLOBALS import *
from ShiftRegister import *
from SPI_Board import *

def get_experimental_design(positions:list[str], frequencies:list[int]):

    raise NotImplementedError

def extract_cell():

    raise NotImplementedError

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

    #Build the test
    get_experimental_design()

    try:
        """
        Rough game plan:
            1. For each cell of design:
            a. Establish connection
            b. Send x values

        So I need something that will grab the cell to test,
        another thing to establish the connection, and lastly something to send the values.

        I also need a logging framework. 
        """
        cell = extract_cell()

        hub.enable_bus()
        
        #Do this repeatedly
        hub.transfer()
    
    except KeyboardInterrupt:
        print("Process terminated by user")
        pi.spi_close(h_spi)
        #break


if __name__ == "__main__":
    
    #Execute the code
    main()
