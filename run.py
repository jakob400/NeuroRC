import os
import graph_build as gbuild
import networkx as nx
from weight_generator import weight_generator
import update_functions
import const
from dynamic_voltage_plot import voltage_plot
from network_plot import network_plot


i=0
if (i == 0):
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')
    print(' =========================================== ')
    print('|-|   NeuroRC: Version 2.3.1              |-|')
    print('|-|   Author: J Weirathmueller            |-|')
    print('|-|   Last Updated: February 26th, 2018   |-|')
    print(' =========================================== ')
    i = i+1

G = gbuild.graph_build()

while True:
    response = input('Which model would you like to use? (STR/LIF)\n')
    if all ([response != 'STR', response != 'LIF']):
        print('Invalid input; Please try again.\n')
    elif (response == 'STR'):
        model = response
        break
    elif (response == 'LIF'):
        model = response
        break

# while True:
#     response = input('How would you like to timekeep? (steps/clock)\n')
#     if all ([response != 'steps', response != 'clock']):
#         print('Invalid input; Please try again.\n')
#     elif (response == 'steps'):
#         timekeeping = response
#         while True:
#             response = input('How many timesteps would you like to take?\n')
#             if (type(response) == str):
#                 print('Invalid input; Please try again.\n')
#             else:
#                 const.tMax = response
#                 break
#             break
#     elif (response == 'clock'):
#         timekeeping = response
#         while True:
#             response = input('How long would you like to simulate for? (1e-3 recommended)\n')
#             if (type(response) == str):
#                 print('Invalid input; Please try again.\n')
#             else:
#                 const.total_time = response
#                 break
#             break

G = gbuild.set_graph_attributes(G,model) # sets node attributes
G = weight_generator(G) # sets edge weights randomly
#timesteps = const.timesteps #len(G.node[1]['voltage'])





#for t in range(timesteps-1): # iterating over timesteps (minus one because it goes as t+1)
time_taken = 0 # Starts at 0.
t = 0 # timestep
tMax = const.tMax # Max timesteps
#while True:
if (model == 'STR'):
    #while True:
    while(t<tMax):
        if True:
        #if (time_taken < const.total_time):
            G, time_taken = update_functions.update_state_STR(G,t)
            t = t + 1
            print('t is  = ',t)
            #network_plot(G,t)
        else:
            break
elif (model == 'LIF'):
    #while True:
    while(t<tMax):
        #print('\r', t,end='')
        #if (time_taken < const.total_time):
        if True:
            G, time_taken = update_functions.update_state_LIF(G,t)
            t = t + 1
            print('t is  = ',t)
        else:
            break


print('Time calculated over = ', time_taken)
print('Time steps taken     = ', len(G.nodes[1]['voltage']),'\n')

print(nx.info(G),'\n')

voltage_plot(G)

#os.system('convert -delay 10 -loop 0 *.png animation.gif')




#Storage of voltages, etc is faulty.
#NeuroRegionCompute
