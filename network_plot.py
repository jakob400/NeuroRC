import os

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def network_plot(G, state, t, out_dir='Animation Files'):
    """Color nodes by voltage at step t. Reads from state.history['V']."""
    voltages = np.asarray(state.history['V'][t])
    pos = nx.shell_layout(G)
    nx.draw_networkx_edges(G, pos, alpha=0.2)
    nc = nx.draw_networkx_nodes(
        G, pos, nodelist=list(G.nodes), node_color=voltages,
        node_size=100, cmap=plt.cm.jet, vmin=-0.07, vmax=0.05,
    )
    plt.colorbar(nc)
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig('%s/%d.png' % (out_dir, t))
    plt.clf()
