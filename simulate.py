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
import integrators
import state as state_mod
import logging_hdf5


def simulate(model, *, N=None, K=None, P=None, tMax=None, seed=0,
             fixed_dt_mode=None, dt_fixed=None, log_dir=None,
             state_init=None):
    if model not in ('STR', 'LIF'):
        raise ValueError("model must be 'STR' or 'LIF', got %r" % (model,))

    random.seed(seed)
    np.random.seed(seed)

    saved = {}
    overrides = {
        'N': N, 'K': K, 'P': P, 'tMax': tMax,
        'fixed_dt_mode': fixed_dt_mode, 'dt_fixed': dt_fixed,
    }
    for key, value in overrides.items():
        if value is not None:
            saved[key] = getattr(const, key)
            setattr(const, key, value)

    try:
        G = graph_build.graph_build()
        G = graph_build.set_graph_attributes(G, model)
        G = weight_generator.weight_generator(G)
        state = state_mod.build_state(G, model)
        if state_init is not None:
            state_init(state)

        step = integrators.step_for(model)
        t_max = const.tMax
        for t in range(t_max):
            step(G, state, t)
        if log_dir is not None:
            logging_hdf5.dump_state(state, model, seed, log_dir=log_dir)
        return G, state
    finally:
        for key, value in saved.items():
            setattr(const, key, value)
