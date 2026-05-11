import random
import const


def weight_generator(G):
    """Assign each edge a uniform random weight in [weight_low, weight_high]."""
    for i, j, _ in G.edges(data=True):
        G[i][j]['weight'] = random.uniform(const.weight_low, const.weight_high)
    return G
