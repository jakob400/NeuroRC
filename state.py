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
from typing import Dict, List, Optional

import numpy as np
from scipy import sparse

import const
from delay_buffer import RingBuffer


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
    V_buffer: Optional[RingBuffer] = None

    @property
    def N(self) -> int:
        return self.V.shape[0]


def build_adjacency(G) -> sparse.csr_matrix:
    """Weighted adjacency. ``A[postsyn, presyn] = w`` so that the recurrent
    input to neuron ``j`` is ``(A @ sigma_delayed)[j] = sum_k A[j,k] * sigma_k``,
    summed over presynaptic ``k``.

    Excludes self-loops. For undirected graphs the second add keeps A
    symmetric (matches Phase 0-2 behaviour). For directed graphs only
    the (postsyn, presyn) entry is set, so reciprocity-free DiGraphs
    yield a one-sided adjacency.
    """
    N = G.number_of_nodes()
    rows, cols, data = [], [], []
    is_directed = G.is_directed()
    for u, v, d in G.edges(data=True):
        if u == v:
            continue
        w = d.get('weight', 1.0)
        rows.append(v); cols.append(u); data.append(w)
        if not is_directed:
            rows.append(u); cols.append(v); data.append(w)
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

    # Ring buffer for delayed voltage lookups. Depth must cover max steps back
    # that delay() can request: bounded by tau_D / dt_min. Use a conservative
    # default of 1024; adaptive-dt simulations with very small epsilon may need
    # more, but the buffer saturates gracefully.
    depth = max(int(const._tau_D / max(const.epsilon / 1e3, 1e-7)) + 16, 128)
    V_buffer = RingBuffer(N=N, depth=min(depth, 8192), fill=const.voltage_init)
    V_buffer.push(V.copy())

    state = State(V=V.copy(), g_A=g_A.copy(), g_E=g_E.copy(), g_I=g_I.copy(),
                  last_spike_time=last_spike, A=A, model=model, V_buffer=V_buffer)

    state.history['V'] = [V.copy()]
    if model == 'STR':
        state.history['g_A'] = [g_A.copy()]
        state.history['g_E'] = [g_E.copy()]
        state.history['g_I'] = [g_I.copy()]
    # Per-neuron RHS magnitudes M[t,j] = max(|f_V|, |f_A|, |f_E|, |f_I|) — the
    # quantity that drives adaptive dt and, by proposal #2, an EWS observable.
    # Initial step has no RHS evaluation yet, so the first row is zero.
    state.history['M'] = [np.zeros(N, dtype=np.float64)]
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
