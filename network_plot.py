import networkx as nx
import matplotlib.pyplot as plt
from itertools import count

def network_plot(G,t):
    #voltages = list(nx.get_node_attributes(G,'voltage').values())
    nodes = G.nodes
    voltages = [G.node[j]['voltage'][t] for j in nodes]

    pos = nx.shell_layout(G)

    ec = nx.draw_networkx_edges(G, pos, alpha=0.2) # edge color
    nc = nx.draw_networkx_nodes(G,pos, nodelist=nodes,  node_color=voltages, with_labels=True, node_size=100, cmap=plt.cm.jet,vmin=-.07, vmax=.05)
    plt.colorbar(nc) # node color

    plt.savefig('Animation Files/%d.png' %(t))
    print('title of png is ',t,'\n')
    plt.clf()



#### TO DO
#Find better colormap
#
#Find better layout for visualization
#
#Do a firing map
#
