"""Headless simulation entry point.

Builds the graph, an initial State, runs the per-timestep update loop,
and returns (G, state).  Tests and batch sweeps call this; run.py wraps
it in an interactive prompt.
"""

import random
import numpy as np

import const
import graph_build
import weight_generator
import update_functions
import state as state_mod


def simulate(model, *, N=None, K=None, P=None, tMax=None, seed=0):
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
        state = state_mod.build_state(G, model)

        step = update_functions.update_state_STR if model == 'STR' else update_functions.update_state_LIF
        t_max = const.tMax
        for t in range(t_max):
            step(G, state, t)
        return G, state
    finally:
        for key, value in saved.items():
            setattr(const, key, value)
