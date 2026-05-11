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
    from delay_buffer import interpolated_lookup
    return interpolated_lookup(state.V_buffer, state.dt_list, const._tau_D)


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
    state.history['M'].append(np.abs(fV1))
    return state, state.current_time


def step_heun_fixed_STR(G, state, t):
    dt = const.dt_fixed
    V_now = state.V
    g_A = state.g_A; g_E = state.g_E; g_I = state.g_I
    g_KIR = state.g_KIR

    V_delayed = _delayed_voltage(state)
    sigma_delayed = fn.sigma_vec(V_delayed)
    sigma_now = fn.sigma_vec(V_now)
    sigmaKIR_now = fn.sigma_KIR_vec(V_now)
    summation = state.A.dot(sigma_delayed)

    # Voltage: Heun RK2 using current conductances; drive recurrent term
    # (sigma_delayed) is the same in both stages. g_KIR (slow K) varies on a
    # ~200 ms timescale -- effectively frozen across one 25 us step.
    def fV(V_):
        excitatory = (const.voltage_E - V_) * g_E
        inhibitory = (const.voltage_I - V_) * g_I
        leakage    = (const.voltage_L - V_) * const.conductance_L
        potassium  = (const.voltage_K - V_) * (const.conductance_K_max * fn.sigma_0_vec(V_)
                                               + g_A + g_KIR)
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
    a_E, a_A, a_I, a_KIR = const._a_E, const._a_A, const._a_I, const._a_KIR
    decay_E = np.exp(-a_E * dt)
    decay_A = np.exp(-a_A * dt)
    decay_I = np.exp(-a_I * dt)
    decay_KIR = np.exp(-a_KIR * dt)

    drive_E = const.I if const.drive_mode == 'constant' else 0.0
    drive_A = a_A * const.w_A * const.conductance_A_max * sigma_now
    drive_I = a_I * const.conductance_I_max * summation
    drive_KIR = a_KIR * const.conductance_KIR_max * sigmaKIR_now

    g_A_next = g_A * decay_A + (drive_A / a_A) * (1.0 - decay_A)
    g_I_next = g_I * decay_I + (drive_I / a_I) * (1.0 - decay_I)
    g_KIR_next = g_KIR * decay_KIR + (drive_KIR / a_KIR) * (1.0 - decay_KIR)

    if const.drive_mode == 'ou':
        # OU exact discretization: bypass AMPA decay; g_E is the cortical
        # drive directly. Clamp to >= 0 (conductance).
        decay_ou = np.exp(-dt / const.ou_tau)
        eta = np.random.standard_normal(size=state.N)
        g_E_next = (const.ou_mean
                    + (g_E - const.ou_mean) * decay_ou
                    + const.ou_sigma * np.sqrt(1.0 - decay_ou * decay_ou) * eta)
        g_E_next = np.maximum(g_E_next, 0.0)
    else:
        g_E_next = g_E * decay_E + (drive_E / a_E) * (1.0 - decay_E)
        if const.drive_mode == 'poisson':
            kicks = np.random.poisson(const.poisson_rate * dt, size=state.N)
            g_E_next = g_E_next + kicks * const.poisson_delta_g_E

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
    fE = -a_E * g_E + drive_E
    fA = -a_A * g_A + drive_A
    fI = -a_I * g_I + drive_I
    fKIR = -a_KIR * g_KIR + drive_KIR
    state.history['M'].append(np.maximum.reduce([np.abs(fV1), np.abs(fA), np.abs(fKIR),
                                                 np.abs(fE), np.abs(fI)]))
    return state, state.current_time


def step_for(model: str):
    """Return the right step callable for (model, const.fixed_dt_mode)."""
    if const.fixed_dt_mode:
        return step_heun_fixed_STR if model == 'STR' else step_heun_fixed_LIF
    return step_euler_adaptive_STR if model == 'STR' else step_euler_adaptive_LIF
