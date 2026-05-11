"""GRAPH-1: weight distribution calibration."""

import math

import networkx as nx
import numpy as np
import pytest

import const
from weight_generator import assign_weights


def _complete_graph(n=200):
    return nx.complete_graph(n)


def test_uniform_back_compat():
    """Default ``distribution='uniform'`` matches the Phase 0-2 behaviour."""
    G = _complete_graph(20)
    assign_weights(G, distribution='uniform')
    weights = [d['weight'] for _, _, d in G.edges(data=True)]
    assert all(const.weight_low <= w <= const.weight_high for w in weights)


def test_lognormal_calibration():
    """Lognormal draws hit Koos 2004 calibration: mean ~500 pS, CV ~1."""
    G = _complete_graph(200)  # ~20k edges -> tight statistics
    rng = np.random.default_rng(0)
    assign_weights(G, distribution='lognormal', rng=rng)
    weights = np.array([d['weight'] for _, _, d in G.edges(data=True)])

    mean = float(weights.mean())
    cv = float(weights.std() / mean)

    target_mean = const.weight_mean_S
    target_cv = const.weight_cv

    assert abs(mean - target_mean) / target_mean < 0.05, mean
    assert abs(cv - target_cv) / target_cv < 0.10, cv
    assert (weights > 0).all()


def test_lognormal_kwargs_override():
    """``mean_S`` and ``cv`` kwargs override const defaults."""
    G = _complete_graph(150)
    rng = np.random.default_rng(0)
    assign_weights(G, distribution='lognormal', rng=rng, mean_S=1.0, cv=0.5)
    weights = np.array([d['weight'] for _, _, d in G.edges(data=True)])
    assert abs(weights.mean() - 1.0) / 1.0 < 0.05
    assert abs((weights.std() / weights.mean()) - 0.5) / 0.5 < 0.15


def test_taverna_d2_to_d1_scaling():
    """D2->D1 edges get a 2x post-draw scale; other directions unchanged."""
    G = nx.DiGraph()
    G.add_node(0, subtype='D2')
    G.add_node(1, subtype='D1')
    G.add_node(2, subtype='D2')
    G.add_node(3, subtype='D1')
    # 0 -> 1 is D2->D1 (scale 2)
    # 1 -> 0 is D1->D2 (no scale)
    # 2 -> 3 is D2->D1 (scale 2)
    # 3 -> 2 is D1->D2 (no scale)
    G.add_edges_from([(0, 1), (1, 0), (2, 3), (3, 2)])
    rng = np.random.default_rng(0)
    assign_weights(G, distribution='lognormal', rng=rng,
                   mean_S=1.0, cv=0.001)
    w_d2_to_d1 = (G[0][1]['weight'] + G[2][3]['weight']) / 2
    w_d1_to_d2 = (G[1][0]['weight'] + G[3][2]['weight']) / 2
    assert abs(w_d2_to_d1 / w_d1_to_d2 - 2.0) < 0.1


def test_snudda_native_passthrough():
    """``snudda_native`` leaves pre-existing weight attrs unchanged."""
    G = nx.DiGraph()
    G.add_edge(0, 1, weight=3.14e-10)
    G.add_edge(1, 0, weight=2.72e-10)
    assign_weights(G, distribution='snudda_native')
    assert G[0][1]['weight'] == 3.14e-10
    assert G[1][0]['weight'] == 2.72e-10


def test_snudda_native_rejects_missing():
    G = nx.DiGraph()
    G.add_edge(0, 1)  # no weight
    with pytest.raises(ValueError):
        assign_weights(G, distribution='snudda_native')


def test_unknown_distribution_rejected():
    G = _complete_graph(5)
    with pytest.raises(ValueError):
        assign_weights(G, distribution='exponential')
