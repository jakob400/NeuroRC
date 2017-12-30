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
    print('|-|   NeuroRC: Version 2.0.8              |-|')
    print('|-|   Author: J Weirathmueller            |-|')
    print('|-|   Last Updated: December 30th, 2017   |-|')
    print(' ===========================================')
    i = i+1

G = graph_build()

G = set_graph_attributes(G) # sets node attributes
G = weight_generator(G) # sets edge weights randomly
timesteps = len(G.node[1]['voltage'])






for t in range(timesteps-1): # iterating over timesteps (minus one because it goes as t+1)
    """
    if (t>0): # Can't do this the first round. Maybe find better way.
        M = max(func_v,func_E,func_I,func_A)
        if (func_v < (const.epsilon * M)): # Does this only if the change is not too great
            G,func_v = math_functions.voltage_update(G,t)
            print(func_v)
        if (func_E < (const.epsilon * M)):
            G,func_E = math_functions.conductance_E_update(G,t)
        if (func_I < (const.epsilon * M)):
            G,func_I = math_functions.conductance_I_update(G,t)
        if (func_A < (const.epsilon * M)):
            G,func_A = math_functions.conductance_A_update(G,t)
    else:
        print(t)
        G,func_v = math_functions.voltage_update(G,t)
        G,func_E = math_functions.conductance_E_update(G,t)
        G,func_I = math_functions.conductance_I_update(G,t)
        G,func_A = math_functions.conductance_A_update(G,t)
    """
    G,func_v = math_functions.voltage_update(G,t)
    G,func_E = math_functions.conductance_E_update(G,t)
    G,func_I = math_functions.conductance_I_update(G,t)
    G,func_A = math_functions.conductance_A_update(G,t)




voltage_plot(G)



#Storage of voltages, etc is faulty.
