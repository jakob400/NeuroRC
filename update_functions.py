import math_functions as fn
import const

def update_state_LIF(G, t):
    """ Master Update Calculation for LIF model """
    t_delayed = fn.delay(t)

    # Initializations:
    M = [None] * len(G.node) # Will have j of these.
    func_v = [None] * len(G.node)

    for j in range(len(G.node)): # for loop over all nodes in G
    # Now Updates:
        voltage_now = G.node[j]['voltage'][t]

    # Func Calculations:
        summation = 0

        for k in G.neighbors(j):
            if(k != j): # Redundant unless MultiGraph
                neighbor_voltages = G.node[k]['voltage'] # copies list of all voltages for specific neighbor
                summation = summation + G[j][k]['weight'] * fn.sigma(neighbor_voltages[t_delayed])#fn.delta(neighbor_voltages,t)
        func_v[j] = const._a_m * (-1 * voltage_now + const.I_ext + const.g_syn * summation)

    # Dynamic Protection:
        M[j] = abs(func_v[j]) # Max value for neuron j

    # Final Dynamic Protection:
    best_dt = const.epsilon / max(M) # Calculates what the dt should be
    # print('the max value is', max(M))
    # print('the best dt is  ', best_dt)
    const.dt_list.append(best_dt) # Appends new dt to list of dt's

    # Main Calculations
    for j in range(len(G.node)):
        G.node[j]['voltage'].append(voltage_now + const.dt_list[-1] * func_v[j])        # Use [-1] or [t]. Equivalent, as both are most recent element


    if(G.node[j]['voltage'][t] > 0.05): ##### TESTING FORCED PERIODICITY
        G.node[j]['voltage'][t] = const.voltage_init

    time_taken = sum(const.dt_list) # sums up all dt's
    return G, time_taken









def update_state_STR(G,t):
    """ Master Update Calculation for STR model """
    t_delayed = fn.delay(t)

    # Initializations:
    M = [None] * len(G.node) # Will have j of these.
    func_v = [None] * len(G.node)
    func_A = [None] * len(G.node)
    func_E = [None] * len(G.node)
    func_I = [None] * len(G.node)


    for j in range(len(G.node)): # for loop over all nodes in G
    # Now Updates:
        voltage_now = G.node[j]['voltage'][t]
        conductance_E_now = G.node[j]['conductance_E'][t]
        conductance_I_now = G.node[j]['conductance_I'][t]
        conductance_A_now = G.node[j]['conductance_A'][t]

        #if(voltage_now > 0.04): ##### TESTING FORCED PERIODICITY
        #    G.node[j]['voltage'][t] = const.voltage_init
        #    voltage_now = G.node[j]['voltage'][t]

    # Preliminary Voltage calculations:
        excitatory = (const.voltage_E - voltage_now) * conductance_E_now
        inhibitory = (const.voltage_I - voltage_now) * conductance_I_now
        leakage = (const.voltage_L - voltage_now) * const.conductance_L # this conductance doesn't evolve or depend on neuron
        potassium = (const.voltage_K - voltage_now) * (const.conductance_K_max * fn.sigma_0(voltage_now) + conductance_A_now)

    # Func Calculations:
        func_v[j] = (1 / const.capacitance) * (excitatory + leakage + inhibitory + potassium) # potassium includes AHP, due to equation
        func_E[j] = (-1 * const._a_E * conductance_E_now + const.I)
        func_A[j] = -1 * const._a_A * conductance_A_now + const._a_A * const.w_A * const.conductance_A_max * fn.sigma(voltage_now)
        summation = 0
        for k in G.neighbors(j):
            if(k != j): # Redundant unless MultiGraph
                neighbor_voltage = G.node[k]['voltage'][t_delayed]
                summation = summation + G[j][k]['weight'] * fn.sigma (neighbor_voltage)
        func_I[j] = (-1 * const._a_I * conductance_I_now + const._a_I * const.conductance_K_max * summation)

    # Randomness Generator
        func_v[j] = func_v[j] #+ fn.get_Rand()
        func_E[j] = func_E[j] #+ fn.get_Rand()
        func_A[j] = func_A[j] #+ fn.get_Rand()
        func_I[j] = func_I[j] #+ fn.get_Rand()

    # Dynamic Protection:
        M[j] = max(abs(func_v[j]), abs(func_A[j]), abs(func_E[j]), abs(func_I[j])) # Calculating max func value for neuron j
    # Final Dynamic Protection:
    best_dt = const.epsilon / max(M) # Calculates what the dt should be
    const.dt_list.append(best_dt) # Appends new dt to list of dt's


    # Main Calculations
    for j in range(len(G.node)):
        G.node[j]['voltage'].append(voltage_now + const.dt_list[-1] * func_v[j])        # Use [-1] or [t]. Should be equivalent.
        G.node[j]['conductance_E'].append(conductance_E_now + const.dt_list[-1] * func_E[j])
        G.node[j]['conductance_I'].append(conductance_I_now + const.dt_list[-1] * func_I[j])
        G.node[j]['conductance_A'].append(conductance_A_now + const.dt_list[-1] * func_A[j])




    time_taken = sum(const.dt_list) # sums up all dt's
    return G, time_taken
