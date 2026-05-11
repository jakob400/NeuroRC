"""GRAPH-2: dispatched graph_build interface."""

import networkx as nx
import pytest

import const
from graph_build import graph_build


def test_nws_default():
    G = graph_build('nws', n_nodes=50, seed=1, k=4, p=0.05)
    assert G.number_of_nodes() == 50
    assert G.graph['source'] == 'nws'
    assert G.graph['seed'] == 1


def test_nws_back_compat_no_args():
    """Calling without graph_type defaults to NWS using const.N/K/P."""
    G = graph_build()
    assert G.number_of_nodes() == const.N
    assert G.graph['source'] == 'nws'


def test_nws_reproducibility():
    G1 = graph_build('nws', n_nodes=80, seed=42, k=6, p=0.1)
    G2 = graph_build('nws', n_nodes=80, seed=42, k=6, p=0.1)
    assert set(G1.edges()) == set(G2.edges())


def test_modular_block_structure():
    G = graph_build('modular', n_nodes=100, seed=0,
                    n_d1=50, n_d2=50)
    assert G.number_of_nodes() == 100
    assert isinstance(G, nx.DiGraph)
    d1 = [n for n, attrs in G.nodes(data=True) if attrs['subtype'] == 'D1']
    d2 = [n for n, attrs in G.nodes(data=True) if attrs['subtype'] == 'D2']
    assert len(d1) == 50 and len(d2) == 50
    # Burke asymmetry: D2->D2 edges should be substantially denser than
    # D1->D2 edges. With block_probs default [[0.14,0.06],[0.27,0.27]] at
    # N=50 per block, expected counts ~ 50*50*p. Statistical, not exact.
    d2_d2 = sum(1 for u, v in G.edges() if u in d2 and v in d2)
    d1_d2 = sum(1 for u, v in G.edges() if u in d1 and v in d2)
    assert d2_d2 > 2 * d1_d2, (d2_d2, d1_d2)


def test_modular_seed_reproducibility():
    G1 = graph_build('modular', n_nodes=80, seed=7)
    G2 = graph_build('modular', n_nodes=80, seed=7)
    assert set(G1.edges()) == set(G2.edges())


def test_unknown_graph_type_rejected():
    with pytest.raises(ValueError):
        graph_build('mystery', n_nodes=10)


def test_ms_rewire_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        graph_build('ms_rewire', n_nodes=20)


def test_gamma_kernel_blocked_without_verification():
    with pytest.raises(AssertionError, match='Yim 2017'):
        graph_build('gamma_kernel', n_nodes=20)


def test_snudda_not_yet_implemented():
    with pytest.raises(NotImplementedError):
        graph_build('snudda', n_nodes=20)
