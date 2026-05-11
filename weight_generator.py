"""Synaptic weight assignment.

GRAPH-1: replaces the uniform-only path with a dispatched assign_weights()
that supports the calibrated Koos 2004 lognormal distribution as the
production default for striatal MSN-MSN synapses, while keeping the
uniform path available for back-compat with the Phase 0-2 baselines.

Lognormal calibration (Koos, Tepper, Wilson 2004):
- Target mean per-synapse conductance ~500 pS
  (V_IPSC ~ 0.5 mV; g = V_IPSC / ((V_I - V_rest) * R_in) with
   R_in = 200 MOhm and (V_I - V_rest) ~ 5 mV -> 0.5 nS = 500 pS)
- Coefficient of variation CV ~ 1.0

For a lognormal X with parameters (mu, sigma):
- mean(X) = exp(mu + sigma**2 / 2)
- CV(X)**2 = exp(sigma**2) - 1
Hence sigma = sqrt(ln(CV**2 + 1));  mu = ln(mean) - sigma**2 / 2.

D1/D2 weight asymmetry (Taverna 2008): when source.subtype='D2' and
target.subtype='D1', the unitary IPSC is roughly 2x larger. Applied as
a post-draw scalar so the lognormal shape is preserved.
"""

import math
import random

import numpy as np

import const


def assign_weights(G, distribution='uniform', rng=None, **kwargs):
    """Attach a ``weight`` attribute to every edge of ``G``.

    Parameters
    ----------
    G : networkx.Graph or networkx.DiGraph
        Graph whose edges will be tagged in-place.
    distribution : {'uniform', 'lognormal', 'snudda_native'}
        - ``'uniform'``: ``rng.uniform(const.weight_low, const.weight_high)``.
          Dimensionless, matches Phase 0-2 behaviour.
        - ``'lognormal'``: Koos 2004 calibrated draw (Siemens). Default
          parameters are ``const.weight_mean_S`` and ``const.weight_cv``;
          override with ``mean_S`` and ``cv`` kwargs.
        - ``'snudda_native'``: leave existing ``weight`` attributes alone;
          for graphs loaded from a Snudda extraction that already carry
          per-edge conductance.
    rng : numpy.random.Generator | None
        Source of randomness. If None, falls back to ``random`` (uniform)
        or ``np.random.default_rng()`` (lognormal).
    kwargs : dict
        ``mean_S``, ``cv`` for the lognormal branch;
        ``d2_to_d1_scale`` (default 2.0) for Taverna asymmetry.

    Returns
    -------
    G
        Same graph, with ``G[u][v]['weight']`` set on every edge.
    """
    if distribution == 'uniform':
        for u, v in G.edges():
            if rng is None:
                w = random.uniform(const.weight_low, const.weight_high)
            else:
                w = float(rng.uniform(const.weight_low, const.weight_high))
            G[u][v]['weight'] = w
        return G

    if distribution == 'snudda_native':
        for u, v, d in G.edges(data=True):
            if 'weight' not in d:
                raise ValueError(
                    'snudda_native requires existing weight attrs '
                    '(missing on edge %r->%r)' % (u, v))
        return G

    if distribution != 'lognormal':
        raise ValueError('unknown distribution %r' % (distribution,))

    mean_S = float(kwargs.get('mean_S', const.weight_mean_S))
    cv = float(kwargs.get('cv', const.weight_cv))
    d2_to_d1_scale = float(kwargs.get('d2_to_d1_scale', 2.0))

    sigma = math.sqrt(math.log(cv * cv + 1.0))
    mu = math.log(mean_S) - 0.5 * sigma * sigma

    if rng is None:
        rng = np.random.default_rng()

    for u, v in G.edges():
        w = float(rng.lognormal(mean=mu, sigma=sigma))
        # Taverna 2008 D2->D1 asymmetry; only applied on modular graphs
        # whose nodes carry a 'subtype' attribute. Other graphs (NWS,
        # Snudda when subtype unset) pass through unscaled.
        u_sub = G.nodes[u].get('subtype')
        v_sub = G.nodes[v].get('subtype')
        if u_sub == 'D2' and v_sub == 'D1':
            w *= d2_to_d1_scale
        G[u][v]['weight'] = w

    return G


def weight_generator(G):
    """Back-compat alias used by the legacy run.py path.

    Phase 0-2 callers expect uniform weights on G; preserve that to keep
    pinned baselines bit-identical until callers migrate to
    ``assign_weights`` explicitly.
    """
    return assign_weights(G, distribution='uniform')
