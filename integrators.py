"""Per-step integrators for STR and LIF.

Two modes, dispatched by const.fixed_dt_mode:

- step_heun_fixed_*: Heun (explicit RK2) on V at const.dt_fixed, plus
  exp-Euler on the conductances (which are linear first-order ODEs with
  slowly-varying drive). Required for proposal #1 / #3 fairness.

- step_euler_adaptive_*: legacy adaptive explicit Euler. The
  update_functions module remains the canonical implementation; this
  module re-exports it under the canonical name.
"""

import numpy as np

import const
import math_functions as fn
import update_functions


step_euler_adaptive_LIF = update_functions.update_state_LIF
step_euler_adaptive_STR = update_functions.update_state_STR


def _delayed_voltage(state):
    i = fn.delay_steps(state)
    return state.V_buffer.at(i)


def _spike_reset(state, V_candidate, current_time):
    in_refr = (current_time - state.last_spike_time) < const.t_refr
    V_next = np.where(in_refr, const.V_reset, V_candidate)
    spike_mask = (~in_refr) & (V_next >= const.V_thresh)
    V_next = np.where(spike_mask, const.V_reset, V_next)
    state.last_spike_time = np.where(spike_mask, current_time, state.last_spike_time)
    return V_next


def step_heun_fixed_LIF(G, state, t):
    dt = const.dt_fixed
    V_now = state.V
    V_delayed = _delayed_voltage(state)
    sigma_delayed = fn.sigma_vec(V_delayed)
    summation = state.A.dot(sigma_delayed)

    fV1 = const._a_m * (-V_now + const.I_ext + const.g_syn * summation)
    V_pred = V_now + dt * fV1
    fV2 = const._a_m * (-V_pred + const.I_ext + const.g_syn * summation)
    V_candidate = V_now + 0.5 * dt * (fV1 + fV2)

    state.dt_list.append(dt)
    state.current_time += dt
    V_next = _spike_reset(state, V_candidate, state.current_time)

    state.V = V_next
    state.V_buffer.push(V_next)
    state.history['V'].append(V_next.copy())
    return state, state.current_time


def step_heun_fixed_STR(G, state, t):
    dt = const.dt_fixed
    V_now = state.V
    g_A = state.g_A; g_E = state.g_E; g_I = state.g_I

    V_delayed = _delayed_voltage(state)
    sigma_delayed = fn.sigma_vec(V_delayed)
    sigma_now = fn.sigma_vec(V_now)
    summation = state.A.dot(sigma_delayed)

    # Voltage: Heun RK2 using current conductances; drive recurrent term
    # (sigma_delayed) is the same in both stages.
    def fV(V_):
        excitatory = (const.voltage_E - V_) * g_E
        inhibitory = (const.voltage_I - V_) * g_I
        leakage    = (const.voltage_L - V_) * const.conductance_L
        potassium  = (const.voltage_K - V_) * (const.conductance_K_max * fn.sigma_0_vec(V_) + g_A)
        return (excitatory + leakage + inhibitory + potassium) / const.capacitance

    fV1 = fV(V_now)
    V_pred = V_now + dt * fV1
    fV2 = fV(V_pred)
    V_candidate = V_now + 0.5 * dt * (fV1 + fV2)

    state.dt_list.append(dt)
    state.current_time += dt
    V_next = _spike_reset(state, V_candidate, state.current_time)

    # exp-Euler for conductances: dg/dt = -a*g + drive  =>
    # g_next = g*exp(-a*dt) + (drive/a)*(1 - exp(-a*dt))
    a_E, a_A, a_I = const._a_E, const._a_A, const._a_I
    decay_E = np.exp(-a_E * dt)
    decay_A = np.exp(-a_A * dt)
    decay_I = np.exp(-a_I * dt)

    drive_E = const.I if const.drive_mode == 'constant' else 0.0
    drive_A = a_A * const.w_A * const.conductance_A_max * sigma_now
    drive_I = a_I * const.conductance_I_max * summation

    g_E_next = g_E * decay_E + (drive_E / a_E) * (1.0 - decay_E)
    g_A_next = g_A * decay_A + (drive_A / a_A) * (1.0 - decay_A)
    g_I_next = g_I * decay_I + (drive_I / a_I) * (1.0 - decay_I)

    if const.drive_mode == 'poisson':
        kicks = np.random.poisson(const.poisson_rate * dt, size=state.N)
        g_E_next = g_E_next + kicks * const.poisson_delta_g_E

    state.V = V_next
    state.g_E = g_E_next
    state.g_I = g_I_next
    state.g_A = g_A_next
    state.V_buffer.push(V_next)
    state.history['V'].append(V_next.copy())
    state.history['g_A'].append(g_A_next.copy())
    state.history['g_E'].append(g_E_next.copy())
    state.history['g_I'].append(g_I_next.copy())
    return state, state.current_time


def step_for(model: str):
    """Return the right step callable for (model, const.fixed_dt_mode)."""
    if const.fixed_dt_mode:
        return step_heun_fixed_STR if model == 'STR' else step_heun_fixed_LIF
    return step_euler_adaptive_STR if model == 'STR' else step_euler_adaptive_LIF
