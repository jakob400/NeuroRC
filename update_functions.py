import numpy as np

import math_functions as fn
import const


def update_state_LIF(G, t):
    """ Master Update Calculation for LIF model """
    t_delayed = fn.delay(G, t)
    dt_list = G.graph['dt_list']

    N = G.number_of_nodes()
    M = [None] * N
    func_v = [None] * N

    for j in range(N):
        voltage_now = G.nodes[j]['voltage'][t]

        summation = 0
        for k in G.neighbors(j):
            if k != j:
                neighbor_voltages = G.nodes[k]['voltage']
                summation += G[j][k]['weight'] * fn.sigma(neighbor_voltages[t_delayed])
        func_v[j] = const._a_m * (-1 * voltage_now + const.I_ext + const.g_syn * summation)

        M[j] = abs(func_v[j])

    best_dt = const.epsilon / max(M)
    dt_list.append(best_dt)
    dt = dt_list[-1]
    current_time = sum(dt_list)

    for j in range(N):
        v_prev = G.nodes[j]['voltage'][t]
        in_refr = (current_time - G.nodes[j]['last_spike_time']) < const.t_refr
        if in_refr:
            v_new = const.V_reset
        else:
            v_new = v_prev + dt * func_v[j]
            if v_new >= const.V_thresh:
                v_new = const.V_reset
                G.nodes[j]['last_spike_time'] = current_time
        G.nodes[j]['voltage'].append(v_new)

    time_taken = current_time
    return G, time_taken


def update_state_STR(G, t):
    """ Master Update Calculation for STR model """
    t_delayed = fn.delay(G, t)
    dt_list = G.graph['dt_list']

    N = G.number_of_nodes()
    M = [None] * N
    func_v = [None] * N
    func_A = [None] * N
    func_E = [None] * N
    func_I = [None] * N

    for j in range(N):
        voltage_now = G.nodes[j]['voltage'][t]
        conductance_E_now = G.nodes[j]['conductance_E'][t]
        conductance_I_now = G.nodes[j]['conductance_I'][t]
        conductance_A_now = G.nodes[j]['conductance_A'][t]

        excitatory = (const.voltage_E - voltage_now) * conductance_E_now
        inhibitory = (const.voltage_I - voltage_now) * conductance_I_now
        leakage = (const.voltage_L - voltage_now) * const.conductance_L
        potassium = (const.voltage_K - voltage_now) * (const.conductance_K_max * fn.sigma_0(voltage_now) + conductance_A_now)

        func_v[j] = (1 / const.capacitance) * (excitatory + leakage + inhibitory + potassium)
        if const.drive_mode == 'constant':
            func_E[j] = -1 * const._a_E * conductance_E_now + const.I
        else:
            func_E[j] = -1 * const._a_E * conductance_E_now
        func_A[j] = -1 * const._a_A * conductance_A_now + const._a_A * const.w_A * const.conductance_A_max * fn.sigma(voltage_now)

        summation = 0
        for k in G.neighbors(j):
            if k != j:
                neighbor_voltage = G.nodes[k]['voltage'][t_delayed]
                summation += G[j][k]['weight'] * fn.sigma(neighbor_voltage)
        func_I[j] = -1 * const._a_I * conductance_I_now + const._a_I * const.conductance_I_max * summation

        M[j] = max(abs(func_v[j]), abs(func_A[j]), abs(func_E[j]), abs(func_I[j]))

    best_dt = const.epsilon / max(M)
    dt_list.append(best_dt)
    dt = dt_list[-1]
    current_time = sum(dt_list)

    if const.drive_mode == 'poisson':
        kicks = np.random.poisson(const.poisson_rate * dt, size=N)
    else:
        kicks = None

    for j in range(N):
        v_prev  = G.nodes[j]['voltage'][t]
        gE_prev = G.nodes[j]['conductance_E'][t]
        gI_prev = G.nodes[j]['conductance_I'][t]
        gA_prev = G.nodes[j]['conductance_A'][t]

        in_refr = (current_time - G.nodes[j]['last_spike_time']) < const.t_refr
        if in_refr:
            v_new = const.V_reset
        else:
            v_new = v_prev + dt * func_v[j]
            if v_new >= const.V_thresh:
                v_new = const.V_reset
                G.nodes[j]['last_spike_time'] = current_time

        gE_new = gE_prev + dt * func_E[j]
        if kicks is not None and kicks[j] > 0:
            gE_new += kicks[j] * const.poisson_delta_g_E

        G.nodes[j]['voltage'].append(v_new)
        G.nodes[j]['conductance_E'].append(gE_new)
        G.nodes[j]['conductance_I'].append(gI_prev + dt * func_I[j])
        G.nodes[j]['conductance_A'].append(gA_prev + dt * func_A[j])

    time_taken = current_time
    return G, time_taken
