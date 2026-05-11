"""Graph topology constructors, dispatched by graph_type.

GRAPH-2 replaces the single-purpose Newman-Watts-Strogatz call with a
dispatched ``graph_build(graph_type=..., n_nodes=..., seed=..., **kwargs)``
front-end that selects one of five constructors. Phase 3 lands them
incrementally:

    nws           - NWS small-world (Watts/Strogatz/Newman lineage)
    modular       - stochastic block model with D1/D2 Burke 2017 asymmetry
    ms_rewire     - Maslov-Sneppen degree-preserving rewire of a source graph
    gamma_kernel  - distance-dependent Gamma kernel (Yim/Aertsen/Kumar 2017)
    snudda        - extracted MSN subgraph from a Snudda .graphml dump

Per-neuron state lives on the State object (see state.py); this module
is only responsible for topology and the per-edge ``weight`` attribute.
"""

import random

import networkx as nx
import numpy as np

import const


def graph_build(graph_type='nws', n_nodes=None, seed=None, **kwargs):
    """Dispatch to a graph constructor and return the result.

    Parameters
    ----------
    graph_type : str
        One of ``'nws'``, ``'modular'``, ``'ms_rewire'``,
        ``'gamma_kernel'``, ``'snudda'``.
    n_nodes : int, optional
        Number of nodes. Defaults to ``const.N`` for back-compat with the
        pre-GRAPH-2 callers.
    seed : int, optional
        Random seed. If None, a uniform integer in [1, 10000) is drawn.
    kwargs : dict
        Per-branch options; see the dispatch table in module docstring.

    Returns
    -------
    networkx graph
        For ``'nws'`` (pre-GRAPH-3) this is still an undirected ``Graph``;
        GRAPH-3 and the other branches return ``DiGraph``. Every graph
        carries ``G.graph['source']`` and ``G.graph['seed']``.
    """
    if n_nodes is None:
        n_nodes = const.N
    if seed is None:
        seed = random.randint(1, 10000)

    if graph_type == 'nws':
        G = _build_nws(n_nodes, seed, **kwargs)
    elif graph_type == 'modular':
        G = _build_modular(n_nodes, seed, **kwargs)
    elif graph_type == 'ms_rewire':
        G = _build_ms_rewire(n_nodes, seed, **kwargs)
    elif graph_type == 'gamma_kernel':
        G = _build_gamma_kernel(n_nodes, seed, **kwargs)
    elif graph_type == 'snudda':
        G = _build_snudda(n_nodes, seed, **kwargs)
    else:
        raise ValueError('unknown graph_type %r' % (graph_type,))

    G.graph['source'] = graph_type
    G.graph['seed'] = seed
    G.graph.setdefault('dt_list', [])
    G.name = G.name or "Jakob's Model Network"
    return G


def _build_nws(n_nodes, seed, **kwargs):
    """Newman-Watts-Strogatz small-world. GRAPH-3 will orient into DiGraph."""
    k = int(kwargs.get('k', const.K))
    p = float(kwargs.get('p', const.P))
    return nx.newman_watts_strogatz_graph(n_nodes, k, p, seed=seed)


def _build_modular(n_nodes, seed, **kwargs):
    """Stochastic block model with Burke 2017 D1/D2 asymmetry.

    Default block_probs reflect Burke, Rotstein, Alvarez (2017) Table 1
    measured at fixed intersomatic distances:
        D1 -> D1: 0.14
        D1 -> D2: 0.06
        D2 -> D1: 0.27
        D2 -> D2: 0.27
    """
    n_d1 = int(kwargs.get('n_d1', n_nodes // 2))
    n_d2 = int(kwargs.get('n_d2', n_nodes - n_d1))
    block_probs = kwargs.get('block_probs',
                             [[0.14, 0.06], [0.27, 0.27]])
    G = nx.stochastic_block_model([n_d1, n_d2], block_probs,
                                  directed=True, seed=seed,
                                  selfloops=False)
    for i in range(n_d1):
        G.nodes[i]['subtype'] = 'D1'
    for i in range(n_d1, n_d1 + n_d2):
        G.nodes[i]['subtype'] = 'D2'
    return G


def _build_ms_rewire(n_nodes, seed, **kwargs):
    raise NotImplementedError(
        'ms_rewire not yet implemented; requires a source_graph kwarg. '
        'See GRAPH-5 in PLAN.md.')


def _build_gamma_kernel(n_nodes, seed, **kwargs):
    if not kwargs.get('gamma_params_verified', False):
        raise AssertionError(
            'Read Yim 2017 Fig. 2 and confirm shape/scale before running; '
            'pass gamma_params_verified=True to the kwargs.')
    raise NotImplementedError(
        'gamma_kernel not yet implemented. See GRAPH-6 in PLAN.md.')


def _build_snudda(n_nodes, seed, **kwargs):
    raise NotImplementedError(
        'snudda branch requires the Docker extraction pipeline; '
        'see scripts/snudda_extract.py (not yet implemented). '
        'See GRAPH-4 in PLAN.md.')


def set_graph_attributes(G, model):
    """No-op kept for API compatibility; per-neuron state lives on State."""
    return G
