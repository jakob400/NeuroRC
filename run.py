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
from voltage_plot import voltage_plot


i=0
if (i == 0):
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('cls' if os.name == 'nt' else 'clear')
    print(' ===========================================')
    print('|-|   NeuroRC: Version 2.0.5              |-|')
    print('|-|   Author: J Weirathmueller            |-|')
    print('|-|   Last Updated: December 21st, 2017   |-|')
    print(' ===========================================')
    i = i+1

G = graph_build()

G = set_graph_attributes(G) # sets node attributes
G = weight_generator(G) # sets edge weights randomly
timesteps = len(G.node[1]['voltage'])

for t in range(timesteps-1): # iterating over timesteps (minus one because it goes as t+1)
    math_functions.voltage_update(G,t)
    math_functions.conductance_E_update(G,t)
    math_functions.conductance_I_update(G,t)






voltage_plot(G)



#Storage of voltages, etc is faulty.
