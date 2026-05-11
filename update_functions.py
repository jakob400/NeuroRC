"""Per-step updates operating on a State (vectorized)."""

import numpy as np

import math_functions as fn
import const


def _delayed_voltage(state, t):
    """Per-neuron voltage at lag tau_D, via the ring buffer with linear interp."""
    from delay_buffer import interpolated_lookup
    return interpolated_lookup(state.V_buffer, state.dt_list, const._tau_D)


def _neighbor_sigma_sum(state, sigma_delayed):
    """sum_k A[j,k] * sigma(V_k_delayed) for every j."""
    return state.A.dot(sigma_delayed)


def update_state_LIF(G, state, t):
    V_now = state.V
    V_delayed = _delayed_voltage(state, t)
    sigma_delayed = fn.sigma_vec(V_delayed)
    summation = _neighbor_sigma_sum(state, sigma_delayed)
    func_v = const._a_m * (-V_now + const.I_ext + const.g_syn * summation)

    M = np.abs(func_v)
    max_mag = float(M.max())
    best_dt = const.dt_max if max_mag == 0 else const.epsilon / max_mag
    best_dt = min(max(best_dt, const.dt_floor), const.dt_max)
    state.dt_list.append(best_dt)
    state.history['M'].append(M.copy())
    dt = best_dt
    state.current_time += dt
    current_time = state.current_time

    in_refr = (current_time - state.last_spike_time) < const.t_refr
    V_next = np.where(in_refr, const.V_reset, V_now + dt * func_v)
    spike_mask = (~in_refr) & (V_next >= const.V_thresh)
    V_next = np.where(spike_mask, const.V_reset, V_next)
    state.last_spike_time = np.where(spike_mask, current_time, state.last_spike_time)

    state.V = V_next
    state.V_buffer.push(V_next)
    state.history['V'].append(V_next.copy())

    return state, current_time


def update_state_STR(G, state, t):
    V_now = state.V
    g_A = state.g_A
    g_E = state.g_E
    g_I = state.g_I
    g_KIR = state.g_KIR

    V_delayed = _delayed_voltage(state, t)
    sigma_delayed = fn.sigma_vec(V_delayed)
    sigma_now = fn.sigma_vec(V_now)
    sigma0_now = fn.sigma_0_vec(V_now)
    sigmaKIR_now = fn.sigma_KIR_vec(V_now)

    excitatory = (const.voltage_E - V_now) * g_E
    inhibitory = (const.voltage_I - V_now) * g_I
    leakage    = (const.voltage_L - V_now) * const.conductance_L
    potassium  = (const.voltage_K - V_now) * (const.conductance_K_max * sigma0_now
                                              + g_A + g_KIR)

    func_v = (excitatory + leakage + inhibitory + potassium) / const.capacitance
    if const.drive_mode == 'constant':
        func_E = -const._a_E * g_E + const.I
    else:
        func_E = -const._a_E * g_E
    func_A = -const._a_A * g_A + const._a_A * const.w_A * const.conductance_A_max * sigma_now
    func_KIR = -const._a_KIR * g_KIR + const._a_KIR * const.conductance_KIR_max * sigmaKIR_now

    summation = _neighbor_sigma_sum(state, sigma_delayed)
    func_I = -const._a_I * g_I + const._a_I * const.conductance_I_max * summation

    M = np.maximum.reduce([np.abs(func_v), np.abs(func_A), np.abs(func_KIR),
                           np.abs(func_E), np.abs(func_I)])
    max_mag = float(M.max())
    best_dt = const.dt_max if max_mag == 0 else const.epsilon / max_mag
    best_dt = min(max(best_dt, const.dt_floor), const.dt_max)
    state.dt_list.append(best_dt)
    state.history['M'].append(M.copy())
    dt = best_dt
    state.current_time += dt
    current_time = state.current_time

    in_refr = (current_time - state.last_spike_time) < const.t_refr
    V_next = np.where(in_refr, const.V_reset, V_now + dt * func_v)
    spike_mask = (~in_refr) & (V_next >= const.V_thresh)
    V_next = np.where(spike_mask, const.V_reset, V_next)
    state.last_spike_time = np.where(spike_mask, current_time, state.last_spike_time)

    if const.drive_mode == 'ou':
        decay_ou = np.exp(-dt / const.ou_tau)
        eta = np.random.standard_normal(size=state.N)
        g_E_next = (const.ou_mean
                    + (g_E - const.ou_mean) * decay_ou
                    + const.ou_sigma * np.sqrt(1.0 - decay_ou * decay_ou) * eta)
        g_E_next = np.maximum(g_E_next, 0.0)
    else:
        g_E_next = g_E + dt * func_E
        if const.drive_mode == 'poisson':
            kicks = np.random.poisson(const.poisson_rate * dt, size=state.N)
            g_E_next = g_E_next + kicks * const.poisson_delta_g_E
    g_I_next = g_I + dt * func_I
    g_A_next = g_A + dt * func_A
    g_KIR_next = g_KIR + dt * func_KIR

    state.V = V_next
    state.g_E = g_E_next
    state.g_I = g_I_next
    state.g_A = g_A_next
    state.g_KIR = g_KIR_next
    state.V_buffer.push(V_next)

    state.history['V'].append(V_next.copy())
    state.history['g_A'].append(g_A_next.copy())
    state.history['g_E'].append(g_E_next.copy())
    state.history['g_I'].append(g_I_next.copy())
    state.history['g_KIR'].append(g_KIR_next.copy())

    return state, current_time
