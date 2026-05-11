"""Vectorized simulation state.

State bundles the per-neuron arrays (V, g_A, g_E, g_I, last_spike_time)
that used to live as Python lists on NetworkX node attributes, plus the
weighted adjacency as a scipy sparse CSR matrix.  History lists are kept
so existing plotting and the delay lookup can still query past values;
NUM-2 swaps the V history for a ring buffer.

The NetworkX graph G is still the source of truth for topology and edge
weights; State is built from it once at the start of a simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from scipy import sparse

import const


NEVER_SPIKED = -1e9


@dataclass
class State:
    V: np.ndarray
    g_A: np.ndarray
    g_E: np.ndarray
    g_I: np.ndarray
    last_spike_time: np.ndarray
    A: sparse.csr_matrix  # weighted adjacency, shape (N, N)
    model: str
    dt_list: List[float] = field(default_factory=list)
    history: Dict[str, List[np.ndarray]] = field(default_factory=dict)
    current_time: float = 0.0

    @property
    def N(self) -> int:
        return self.V.shape[0]


def build_adjacency(G) -> sparse.csr_matrix:
    """Weighted adjacency. Excludes self-loops; consistent with k != j neighbor logic."""
    N = G.number_of_nodes()
    rows, cols, data = [], [], []
    for u, v, d in G.edges(data=True):
        if u == v:
            continue
        w = d.get('weight', 1.0)
        rows.append(u); cols.append(v); data.append(w)
        rows.append(v); cols.append(u); data.append(w)  # undirected
    return sparse.csr_matrix((data, (rows, cols)), shape=(N, N))


def build_state(G, model: str) -> State:
    if model not in ('STR', 'LIF'):
        raise ValueError(model)
    N = G.number_of_nodes()
    V = np.full(N, const.voltage_init, dtype=np.float64)
    if model == 'STR':
        g_A = np.full(N, const.conductance_A_init, dtype=np.float64)
        g_E = np.full(N, const.conductance_E_init, dtype=np.float64)
        g_I = np.full(N, const.conductance_I_init, dtype=np.float64)
    else:
        # LIF has no conductances but we keep zero arrays so update code is uniform.
        g_A = np.zeros(N, dtype=np.float64)
        g_E = np.zeros(N, dtype=np.float64)
        g_I = np.zeros(N, dtype=np.float64)

    last_spike = np.full(N, NEVER_SPIKED, dtype=np.float64)
    A = build_adjacency(G)

    state = State(V=V.copy(), g_A=g_A.copy(), g_E=g_E.copy(), g_I=g_I.copy(),
                  last_spike_time=last_spike, A=A, model=model)

    state.history['V'] = [V.copy()]
    if model == 'STR':
        state.history['g_A'] = [g_A.copy()]
        state.history['g_E'] = [g_E.copy()]
        state.history['g_I'] = [g_I.copy()]
    return state


def record_step(state: State) -> None:
    state.history['V'].append(state.V.copy())
    if state.model == 'STR':
        state.history['g_A'].append(state.g_A.copy())
        state.history['g_E'].append(state.g_E.copy())
        state.history['g_I'].append(state.g_I.copy())


def stack_history(state: State, key: str) -> np.ndarray:
    """Return history[key] as (n_steps, N) ndarray."""
    return np.array(state.history[key])
