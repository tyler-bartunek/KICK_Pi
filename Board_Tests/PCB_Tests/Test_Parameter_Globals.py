## Testing logic variables
#Rates to test
rates = [1.5e6, 3e6, 4.5e6, 6e6, 7.5e6, 9e6]
labeled_rate_dict = dict(zip(['A','B','C','D','E','F'], rates))

sequence_freq_keys = {0:['A', 'B', 'F', 'C', 'E', 'D'],
                      1:['B', 'C', 'A', 'D', 'F', 'E'],
                      2:['C', 'D', 'B', 'E', 'A', 'F'],
                      3:['D', 'E', 'C', 'F', 'B', 'A'],
                      4:['E', 'F', 'D', 'A', 'C', 'B'],
                      5:['F', 'A', 'E', 'B', 'D', 'C']}
sequence_dict = {seq:[labeled_rate_dict[key] for key in sequence_freq_keys[seq]]for seq in sequence_freq_keys.keys()}

#Locations and replicates in a dict
#Locations are from 0-5 locations on the board starting from RL and
#proceeding clockwise, with 9 representing the direct connection case.
replicate_dict = {0:[0, 9, 4, 3, 2, 5, 1],
                  1:[5, 0, 3, 9, 4, 1, 2],
                  2:[4, 3, 2, 1, 5, 0, 9],
                  3:[3, 2, 1, 5, 0, 9, 4],
                  4:[2, 5, 9, 4, 1, 3, 0],
                  5:[9, 1, 0, 2, 3, 4, 5],
                  6:[1, 4, 5, 0, 9, 2, 3]}