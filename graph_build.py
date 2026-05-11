import networkx as nx
from weight_generator import weight_generator
import random
import const

def graph_build():
	"""Builds a Newmann-Watts-Strogatz graph"""
	seed_no = random.randint(1, 10000)
	G = nx.newman_watts_strogatz_graph(const.N,const.K,const.P,seed=seed_no)
	G.name = 'Jakob\'s Model Network'
	G.graph['dt_list'] = []
	return G

def set_graph_attributes(G,model):
	"""Sets initial graph parameters according to model. LIF only requires voltage update while STR requires conducdtance updates."""
	#timelist = [0] * const.timesteps # makes 0-list of size 'timesteps'
	v0 = const.voltage_init # Importing initial voltage parameter.
	gA0 = const.conductance_A_init
	gE0 = const.conductance_E_init
	gI0 = const.conductance_I_init
	if (model == 'STR'):
		for j in range(G.number_of_nodes()): # Iterating over all nodes, to set initial parameters.
			G.nodes[j].update({'voltage' : [v0]})
			G.nodes[j].update({'conductance_A' : [gA0]})
			G.nodes[j].update({'conductance_E' : [gE0]})
			G.nodes[j].update({'conductance_I' : [gI0]})
	if (model == 'LIF'):
		for j in range(G.number_of_nodes()): # Iterating over all nodes, to set initial parameters.
			timelistv = [v0]
			G.nodes[j].update({'voltage' : timelistv})
	return G

# Future work:
#
