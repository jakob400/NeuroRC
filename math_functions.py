import numpy as np

import const


def sigma(voltage_now):
    """Scalar sigma; kept for backwards compatibility."""
    return 1.0 / (1.0 + np.exp(const._beta * (const.voltage_thresh - voltage_now)))


def sigma_0(voltage_now):
    """Scalar sigma_0; kept for backwards compatibility."""
    return 1.0 / (1.0 + np.exp(const._k * (const.voltage_0 - voltage_now)))


def sigma_vec(V):
    """Vectorized sigma over an ndarray of voltages."""
    return 1.0 / (1.0 + np.exp(const._beta * (const.voltage_thresh - V)))


def sigma_0_vec(V):
    """Vectorized sigma_0."""
    return 1.0 / (1.0 + np.exp(const._k * (const.voltage_0 - V)))


def delay_steps(state):
    """Number of steps back that span at least _tau_D of cumulative dt."""
    dt_list = state.dt_list
    dt_sum = 0.0
    i = 0
    n = len(dt_list)
    while dt_sum < const._tau_D and i < n:
        dt_sum += dt_list[-i - 1]
        i += 1
    return i


def delay(state, t):
    """Index into a per-step history list for a delayed voltage. Returns t-i."""
    return t - delay_steps(state)
