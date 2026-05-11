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
    """Newman-Watts-Strogatz small-world, oriented into a DiGraph.

    Each undirected NWS edge {u, v} is assigned a single direction by
    Bernoulli(0.5). The resulting graph has near-zero reciprocity,
    matching empirical MSN-MSN reciprocity ~5-10% (Tunstall et al.
    2002). Mean undirected degree of the source NWS is
    ``k + 2 * p * (N - k - 1)``, not ``k``.
    """
    k = int(kwargs.get('k', const.K))
    p = float(kwargs.get('p', const.P))
    undirected = nx.newman_watts_strogatz_graph(n_nodes, k, p, seed=seed)
    rng = np.random.default_rng(seed)
    G = nx.DiGraph()
    G.add_nodes_from(undirected.nodes())
    for u, v in undirected.edges():
        if rng.random() < 0.5:
            G.add_edge(u, v)
        else:
            G.add_edge(v, u)
    return G


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
    """Maslov-Sneppen degree-preserving rewire of a source DiGraph.

    Runs ``directed_edge_swap`` in chunks and tracks transitivity per
    chunk. Reports a warning when the plateau check fails: if the
    spread of transitivity over the last half of the chunks is more
    than 1% of the (initial - final) drop, the mixer probably didn't
    converge and the swap budget should be doubled.

    Kwargs:
        source_graph (DiGraph, required) - graph to rewire.
        n_swaps_multiplier (int, default 100) - target n_swaps = m * |E|.
        n_chunks (int, default 20).
        weighted (bool, default False) - preserves the existing weight
            attribute via shuffle (not strength-preserving null).
    """
    source = kwargs.get('source_graph')
    if source is None:
        raise ValueError('ms_rewire requires a source_graph kwarg')
    if not isinstance(source, nx.DiGraph):
        raise ValueError('source_graph must be a DiGraph (got %s)'
                         % type(source).__name__)
    if source.number_of_nodes() != n_nodes:
        raise ValueError('source_graph has %d nodes; expected %d'
                         % (source.number_of_nodes(), n_nodes))

    n_swaps_multiplier = int(kwargs.get('n_swaps_multiplier', 100))
    n_chunks = int(kwargs.get('n_chunks', 20))
    weighted = bool(kwargs.get('weighted', False))

    H = source.copy()
    n_edges = H.number_of_edges()
    if n_edges == 0:
        return H

    target_swaps = n_swaps_multiplier * n_edges
    swaps_per_chunk = max(target_swaps // n_chunks, 3)
    rng = np.random.default_rng(seed)

    transitivity_log = [nx.transitivity(H.to_undirected())]
    chunk_seed_max = 2 ** 31 - 1
    for _ in range(n_chunks):
        chunk_seed = int(rng.integers(0, chunk_seed_max))
        try:
            nx.algorithms.swap.directed_edge_swap(
                H, nswap=swaps_per_chunk,
                max_tries=swaps_per_chunk * 10,
                seed=chunk_seed)
        except nx.NetworkXAlgorithmError:
            # Hit the max-tries ceiling without completing the chunk.
            # Continue with whatever swaps did succeed.
            pass
        transitivity_log.append(nx.transitivity(H.to_undirected()))

    # Plateau check: spread over the second half should be << total drop.
    tlog = np.asarray(transitivity_log)
    half = tlog[n_chunks // 2:]
    drop = abs(tlog[0] - tlog[-1])
    spread = float(half.max() - half.min())
    if drop > 1e-9 and spread > 0.01 * drop:
        import warnings
        warnings.warn(
            'ms_rewire plateau check warning: transitivity spread %.4g '
            'over last %d chunks exceeds 1%% of total drop %.4g; '
            'consider doubling n_swaps_multiplier (current=%d)'
            % (spread, len(half), drop, n_swaps_multiplier),
            stacklevel=2)

    H.graph['rewire_transitivity_log'] = transitivity_log
    if weighted:
        # Default behaviour preserves whatever weight attrs survive the
        # swap (NetworkX moves them with the edge). Nothing extra to do
        # here; the strength-preserving Rubinov & Sporns 2011 null is
        # tracked separately.
        pass
    return H


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
