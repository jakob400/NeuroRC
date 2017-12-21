from os import system
import os
from graph_build import graph_build, set_graph_attributes
from weight_generator import weight_generator
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from networkx.drawing.nx_agraph import graphviz_layout
import pygraphviz
import csv
import math_functions
import const


i=0
if (i == 0):
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')
    print(' ===========================================')
    print('|-|   NeuroRC: Version 2.0.1              |-|')
    print('|-|   Author: J Weirathmueller            |-|')
    print('|-|   Last Updated: December 20th, 2017   |-|')
    print(' ===========================================')
    i = i+1

while True:
    response = input('Would you like to generate a new graph? (y/n)\n')
    if (response == 'y'):
        G = graph_build()
        while True:
            response = input('What would you like to title the file?\n')
            if (response[-5:] == '.gexf'):
                #nx.write_gexf(G, response)
                #print('file written to' , response)
                break
            else:
                print('incorrect file type\n')
        break
    elif (response == 'n'):
        while True:
            response = input('What file would you like to open?\n')
            if os.path.exists(response):
                print('File exists.\n')
                G = nx.read_gexf(response)
                break
            else:
                print('Path does not exist.\n')
        break

print(nx.info(G))
#nx.write_gexf(G, 'graph.gexf')




G = set_graph_attributes(G) # sets node attributes
G = weight_generator(G) # sets edge weights randomly
timesteps = len(G.node[1]['voltage'])

for t in range(timesteps-1): # iterating over timesteps (minus one because it goes as t+1)
    print('time is',t)
    math_functions.voltage_update(G,t)
    math_functions.conductance_E_update(G,t)
    math_functions.conductance_I_update(G,t)


xvalues = np.linspace(0, const.dt * timesteps , timesteps)
yvalues = G.node[1]['voltage']

plt.plot(xvalues,yvalues,linestyle='--')
plt.xlabel('Time',fontsize=14)
plt.ylabel('Voltage (V)',fontsize=14)
plt.show()

# pos = graphviz_layout(G, prog='dot')
# nx.draw(G, pos)
# plt.show()




#dependency injection
#classes
