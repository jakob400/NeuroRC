"""Headless simulation entry point.

Wraps graph construction, attribute initialization, weight assignment and
the per-timestep update loop into a single callable so that tests and
batch runs do not have to duplicate run.py.
"""

import random
import numpy as np

import const
import graph_build
import weight_generator
import update_functions


def simulate(model, *, N=None, K=None, P=None, tMax=None, seed=0):
    """Run a simulation and return the final graph.

    Any of N/K/P/tMax overrides the corresponding value in const.py for
    the duration of the call. seed seeds both random and numpy so graph
    topology, weights, and any stochastic dynamics are reproducible.
    """
    if model not in ('STR', 'LIF'):
        raise ValueError("model must be 'STR' or 'LIF', got %r" % (model,))

    random.seed(seed)
    np.random.seed(seed)

    saved = {}
    overrides = {'N': N, 'K': K, 'P': P, 'tMax': tMax}
    for key, value in overrides.items():
        if value is not None:
            saved[key] = getattr(const, key)
            setattr(const, key, value)

    try:
        G = graph_build.graph_build()
        G = graph_build.set_graph_attributes(G, model)
        G = weight_generator.weight_generator(G)

        step = update_functions.update_state_STR if model == 'STR' else update_functions.update_state_LIF
        t_max = const.tMax
        t = 0
        while t < t_max:
            G, _ = step(G, t)
            t += 1
        return G
    finally:
        for key, value in saved.items():
            setattr(const, key, value)
