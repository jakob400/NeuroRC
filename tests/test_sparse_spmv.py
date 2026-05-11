"""NUM-4: verify state.A.dot(sigma_delayed) matches the legacy per-neuron loop."""

import random

import numpy as np

import const
import graph_build
import weight_generator
import state as state_mod
import math_functions as fn


def test_spmv_matches_python_loop_N10():
    random.seed(7)
    np.random.seed(7)
    saved = (const.N, const.K, const.P)
    const.N, const.K, const.P = 10, 3, 0.3
    try:
        G = graph_build.graph_build()
        G = graph_build.set_graph_attributes(G, 'STR')
        G = weight_generator.weight_generator(G)
        state = state_mod.build_state(G, 'STR')
    finally:
        const.N, const.K, const.P = saved

    rng = np.random.default_rng(42)
    V = rng.uniform(-90e-3, -30e-3, size=state.N)
    sigma_v = fn.sigma_vec(V)

    # SpMV
    summ_sparse = state.A.dot(sigma_v)

    # Reference: explicit per-neuron loop over neighbors with k != j
    summ_loop = np.zeros(state.N)
    for j in range(state.N):
        s = 0.0
        for k in G.neighbors(j):
            if k == j:
                continue
            s += G[j][k]['weight'] * sigma_v[k]
        summ_loop[j] = s

    assert np.allclose(summ_sparse, summ_loop, atol=1e-12, rtol=0), (
        'SpMV / loop mismatch: max abs diff = %g' % np.abs(summ_sparse - summ_loop).max()
    )
