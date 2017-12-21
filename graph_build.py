import networkx as nx
from weight_generator import weight_generator
import random

def graph_build():
	N = 250  # number of nodes
	K = 230  # average degree
	P = 5 * 10e-2

	seed_no = random.uniform(1,10000)
	G = nx.newman_watts_strogatz_graph(N,K,P,seed=seed_no)
	G.name = 'Jakob\'s Model Network'

	return G

def set_graph_attributes(G):

	timesteps = 10
	timelist = [0] * timesteps # makes 0-list of size 'timesteps'

	for j in range(len(G.node)):
		G.node[j].update({'voltage' : timelist})
		G.node[j].update({'conductance_A' : timelist})
		G.node[j].update({'conductance_E' : timelist})
		G.node[j].update({'conductance_I' : timelist})

	return G


# Future work:
#
# Make more node attributes than just voltage
# Make better initial values (nonzero) for attribute tuples




# ** nx.set_node_attributes(G, timetuple, 'voltage') **
# Does:
#
# G.node[i][j][k], where
# i : node number
# j : node attribute
# k : time step
