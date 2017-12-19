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
