import networkx as nx
from weight_generator import weight_generator
import random
import const

def graph_build():

	seed_no = random.uniform(1,10000)
	G = nx.newman_watts_strogatz_graph(const.N,const.K,const.P,seed=seed_no)
	G.name = 'Jakob\'s Model Network'

	return G

def set_graph_attributes(G):

	#timelist = [0] * const.timesteps # makes 0-list of size 'timesteps'

	for j in range(len(G.node)):
		timelistv = [0] * const.timesteps # makes 0-list of size 'timesteps'
		timelistcA = [0] * const.timesteps # makes 0-list of size 'timesteps'
		timelistcE = [0] * const.timesteps # makes 0-list of size 'timesteps'
		timelistcI = [0] * const.timesteps # makes 0-list of size 'timesteps'
		G.node[j].update({'voltage' : timelistv})
		G.node[j].update({'conductance_A' : timelistcA})
		G.node[j].update({'conductance_E' : timelistcE})
		G.node[j].update({'conductance_I' : timelistcI})

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
