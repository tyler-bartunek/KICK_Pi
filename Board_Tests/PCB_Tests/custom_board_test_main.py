#Imports
import pigpio
import random

#From adjacent files
from BOARD_GLOBALS import *
from ShiftRegister import ShiftRegister
from SPI_Board import SPIHub

def SetupLogging():

    raise NotImplementedError

def TestLocation(spi_hub:SPIHub, sequence_list:list, Test, num_vals:int = 1000):

    #Set the frequency
    for seq in sequence_list:
        for freq in sequence_dict[seq]:
                        
            #Enable the bus
            spi_hub.enable_bus(0, freq)

            #Execute test
            Test(spi_hub, num_vals)

            #Disable hub for next frequency
            spi_hub.disable_bus()


def EchoTest(spi_hub, num_iters = 1000):

    for val in range(num_vals):
        #Pick a random vaue to send
        test_value = random.randint(0,255)

        #Send the random value twice, log second value received
        for i in range(2):
            received_value = spi_hub.transfer(test_value)


def connect_pigpio():
    #Creates the pigpio object, sets it up and returns it
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    return pi

def main():

    #Initialize the pigpio daemon
    pi = connect_pigpio()
    
    #Initialize the ShiftRegister object
    shift = ShiftRegister(pi, DATA, LATCH, SHIFT_CLK, OE)
    
    #Initialize the Board class
    hub = SPIHub(pi, shift)

    #Run through the test as defined in globals
    try:
        """
        Game plan:
            1. For each cell of design:
                a. Establish connection
                b. Send and receive values for comparison

        I also need a logging framework. 
        """

        reps, sequences = list(range(7)), list(range(8))

        #TODO: Add logging component

        #Get the location
        for rep in reps:
            for loc in replicate_dict[rep]: 

                rx = 0 

                #Set frequency low as possible, send 0xFF
                while rx != b'\xFF':
                    rx = hub.transfer(loc, CHANNEL, rates[0])

                #Established connection, disable hub to reset freq
                hub.disable_bus()
            
                #Run echo test over all frequencies
                test_type = lambda spi_hub: EchoTest(hub)
                TestLocation(hub, sequences, test_type)
    
    except KeyboardInterrupt:
        print("Process terminated by user")
        pi.spi_close(h_spi)
        #break


if __name__ == "__main__":
    
    #Execute the code
    main()
