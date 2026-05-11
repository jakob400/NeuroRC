"""NWS graph construction. Per-neuron state lives on the State object
(see state.py); this module is now only responsible for topology and
weighted edges.
"""

import random

import networkx as nx

import const


def graph_build():
    """Builds a Newman-Watts-Strogatz graph."""
    seed_no = random.randint(1, 10000)
    G = nx.newman_watts_strogatz_graph(const.N, const.K, const.P, seed=seed_no)
    G.name = "Jakob's Model Network"
    G.graph['dt_list'] = []
    return G


def set_graph_attributes(G, model):
    """No-op kept for API compatibility; per-neuron state lives on State."""
    return G
