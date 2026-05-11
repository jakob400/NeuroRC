"""Numerical regression tests pinning the LIF baseline trace."""

from pathlib import Path

import numpy as np

from simulate import simulate

BASELINES = Path(__file__).parent / 'baselines'


def test_lif_n2_baseline_matches():
    G = simulate('LIF', N=2, K=1, P=1e-5, tMax=1000, seed=0)
    V = np.array([G.nodes[j]['voltage'] for j in range(G.number_of_nodes())])
    expected = np.load(BASELINES / 'lif_n2_k1_t1000_seed0.npy')

    assert V.shape == expected.shape, (V.shape, expected.shape)
    assert np.allclose(V, expected, rtol=0, atol=1e-9), (
        'LIF baseline drift: max abs diff = %g' % np.abs(V - expected).max()
    )


def test_lif_deterministic_across_runs():
    """Two runs with the same seed must produce identical traces."""
    G1 = simulate('LIF', N=2, K=1, P=1e-5, tMax=100, seed=42)
    G2 = simulate('LIF', N=2, K=1, P=1e-5, tMax=100, seed=42)
    v1 = np.array(G1.nodes[0]['voltage'])
    v2 = np.array(G2.nodes[0]['voltage'])
    assert np.array_equal(v1, v2)
