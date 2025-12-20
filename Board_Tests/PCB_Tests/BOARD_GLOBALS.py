
###PINS AND OTHER CONSTANTS

#SPI Pins
SPI0_SCLK = 11
CHANNEL = 0
CIPO = 9
COPI = 10

#Shift register pins
LATCH = 5 
DATA = 6
SHIFT_CLK = 13
OE = 26

## Testing logic variables
#Rates to test
MCU_CLK_RATE = 250e6
divisor_powers = [16, 13, 11, 9, 7, 5, 3, 1]
rates = [MCU_CLK_RATE / (2 ** div) for div in divisor_powers]
labeled_rate_dict = dict(zip(['A','B','C','D','E','F', 'G', 'H'], rates))

sequence_freq_keys = {0:['A', 'B', 'H', 'C', 'G', 'D', 'F', 'E'],
                      1:['B', 'C', 'A', 'D', 'H', 'E', 'G', 'F'],
                      2:['C', 'D', 'B', 'E', 'A', 'F', 'H', 'G'],
                      3:['D', 'E', 'C', 'F', 'B', 'G', 'A', 'H'],
                      4:['E', 'F', 'D', 'G', 'C', 'H', 'B', 'A'],
                      5:['F', 'G', 'E', 'H', 'D', 'A', 'C', 'B'],
                      6:['G', 'H', 'F', 'A', 'E', 'B', 'D', 'C'],
                      7:['H', 'A', 'G', 'B', 'F', 'C', 'E', 'D']}
sequence_dict = {seq:[labeled_rate_dict[key] for key in sequence_freq_keys[seq]]for seq in sequence_freq_keys.keys()}

#Locations and replicates in a dict
locations = dict(zip(list(range(7)), ['RL', 'CL', 'FL', 'FR', 'CR', 'RR','XX']))
replicate_loc_key_dict = {0:[0, 6, 4, 3, 2, 5, 1],
                          1:[5, 0, 3, 6, 4, 1, 2],
                          2:[4, 3, 2, 1, 5, 0, 6],
                          3:[3, 2, 1, 5, 0, 6, 4],
                          4:[2, 5, 6, 4, 1, 3, 0],
                          5:[6, 1, 0, 2, 3, 4, 5],
                          6:[1, 4, 5, 0, 6, 2, 3]}
replicate_dict = {rep:[locations[key] for key in replicate_loc_key_dict[rep]] for rep in replicate_loc_key_dict.keys()}
