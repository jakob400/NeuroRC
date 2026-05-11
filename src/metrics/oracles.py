"""Ground-truth oracles for proposal #2.

For the cheap pilot (synchronization-onset NWS K-sweep), the oracle is
the Kuramoto order parameter ``R(t)`` of the Hilbert-transformed Vm
traces. ``R`` ranges in [0, 1]; 0 is fully desynchronized, 1 is
phase-locked. A transition is declared the first time ``R`` crosses
0.5 sustained for at least ``min_dwell_ms`` (default 50 ms) per
Proposal #2.
"""

import numpy as np
from scipy import signal as sp_signal


def kuramoto_order(V_history, dt, detrend=True):
    """Per-step Kuramoto order parameter from per-neuron Vm.

    Parameters
    ----------
    V_history : ndarray, shape (n_steps, N)
        Voltage trace.
    dt : float
        Fixed timestep in seconds.
    detrend : bool
        Subtract each neuron's mean Vm before Hilbert. Recommended for
        Vm signals because the DC offset dominates the analytic signal.

    Returns
    -------
    R : ndarray, shape (n_steps,)
        Kuramoto order parameter time series.
    """
    V = np.asarray(V_history, dtype=np.float64)
    if detrend:
        V = V - V.mean(axis=0, keepdims=True)
    analytic = sp_signal.hilbert(V, axis=0)
    phases = np.angle(analytic)
    R = np.abs(np.exp(1j * phases).mean(axis=1))
    return R


def first_crossing(signal_1d, threshold, min_dwell_steps=0):
    """Index of the first sustained threshold crossing, or -1 if none.

    A crossing is "sustained" if the signal stays above ``threshold``
    for at least ``min_dwell_steps`` samples.
    """
    x = np.asarray(signal_1d)
    above = x >= threshold
    if not above.any():
        return -1
    if min_dwell_steps <= 1:
        return int(np.argmax(above))
    # Find runs of True with length >= min_dwell_steps.
    diff = np.diff(above.astype(np.int8), prepend=0, append=0)
    starts = np.flatnonzero(diff == 1)
    ends = np.flatnonzero(diff == -1)
    for s, e in zip(starts, ends):
        if e - s >= min_dwell_steps:
            return int(s)
    return -1
