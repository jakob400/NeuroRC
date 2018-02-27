import networkx as nx
from weight_generator import weight_generator
import random
import const

def graph_build():
	"""Builds a Newmann-Watts-Strogatz graph"""
	seed_no = random.uniform(1,10000)
	G = nx.newman_watts_strogatz_graph(const.N,const.K,const.P,seed=seed_no)
	G.name = 'Jakob\'s Model Network'
	return G

def set_graph_attributes(G,model):
	"""Sets initial graph parameters according to model. LIF only requires voltage update while STR requires conducdtance updates."""
	#timelist = [0] * const.timesteps # makes 0-list of size 'timesteps'
	v0 = const.voltage_init # Importing initial voltage parameter.
	if (model == 'STR'):
		for j in range(len(G.node)): # Iterating over all nodes, to set initial parameters.
			timelistv = [v0] # Doing this step separately for readability.
			timelistcA = [0]
			timelistcE = [0]
			timelistcI = [0]
			G.node[j].update({'voltage' : timelistv})
			G.node[j].update({'conductance_A' : timelistcA})
			G.node[j].update({'conductance_E' : timelistcE})
			G.node[j].update({'conductance_I' : timelistcI})
	if (model == 'LIF'):
		for j in range(len(G.node)): # Iterating over all nodes, to set initial parameters.
			timelistv = [v0]
			G.node[j].update({'voltage' : timelistv})
	return G

# Future work:
#
