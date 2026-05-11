"""Numerical regression tests pinning the LIF baseline trace."""

from pathlib import Path

import numpy as np

from simulate import simulate

BASELINES = Path(__file__).parent / 'baselines'


def _voltage_history(state):
    """Return voltage history as (N, n_steps) to match the legacy baseline shape."""
    return np.array(state.history['V']).T


def test_lif_n2_baseline_matches():
    G, state = simulate('LIF', N=2, K=1, P=1e-5, tMax=1000, seed=0)
    V = _voltage_history(state)
    expected = np.load(BASELINES / 'lif_n2_k1_t1000_seed0.npy')

    assert V.shape == expected.shape, (V.shape, expected.shape)
    assert np.allclose(V, expected, rtol=0, atol=1e-9), (
        'LIF baseline drift: max abs diff = %g' % np.abs(V - expected).max()
    )


def test_lif_deterministic_across_runs():
    G1, s1 = simulate('LIF', N=2, K=1, P=1e-5, tMax=100, seed=42)
    G2, s2 = simulate('LIF', N=2, K=1, P=1e-5, tMax=100, seed=42)
    v1 = np.array(s1.history['V']).T
    v2 = np.array(s2.history['V']).T
    assert np.array_equal(v1, v2)
