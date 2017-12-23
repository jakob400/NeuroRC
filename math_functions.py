import math
import const

#time division is dt

def sigma_fn(voltage_now):
    """ Regular sigma calculation """
    result = math.pow(1 + math.exp(const._beta * (const.voltage_thresh - voltage_now)), -1) #figure out what _beta should be
    return result

def sigma_0_fn(voltage_now):
    """ Sigma_0 calculation """
    result = math.pow(1 + math.exp(const._k * (const.voltage_0 - voltage_now)), -1)
    return result


def voltage_update(G,t):
    """Voltage Update Euler Calculation. No AHP calculation included"""

    # Now Updates:
    for j in range(len(G.node)):
        voltage_now = G.node[j]['voltage'][t] # maybe change to 'G.nodes[]' later
        conductance_E_now = G.node[j]['conductance_E'][t]
        conductance_I_now = G.node[j]['conductance_I'][t]
        conductance_A_now = G.node[j]['conductance_A'][t]

    # Preliminary calculations:
        excitatory = (const.voltage_E - voltage_now) * conductance_E_now
        inhibitory = (const.voltage_I - voltage_now) * conductance_I_now
        leakage = (const.voltage_L - voltage_now) * const.conductance_L #this conductance doesn't evolve or depend on neuron
        potassium = (const.voltage_K - voltage_now) * (const.conductance_K_max * sigma_0_fn(voltage_now) + conductance_A_now)

    # Main Calculations:
        function = ( 1 / const.capacitance) * (excitatory + leakage + inhibitory + potassium ) #potassium includes AHP, due to equation
        G.node[j]['voltage'][t+1] = voltage_now + const.dt * function 
    return function




def conductance_E_update(G,t):
    """Excitatory Conductance Update Euler Calculation."""
    # Now Updates:
    for j in range(len(G.node)):
        voltage_now = G.node[j]['voltage'][t] # maybe change to 'G.nodes[]' later
        conductance_E_now = G.node[j]['conductance_E'][t]
        conductance_I_now = G.node[j]['conductance_I'][t]
    # Main Calculations:
        function = (-1 * const._a_E * conductance_E_now + const.I)
        G.node[j]['conductance_E'][t+1] = conductance_E_now + const.dt * function
    return function

def conductance_I_update(G,t):
    """Inhibitory Conductance Update Euler Calculation"""
    # Now Updates:
    for j in range(len(G.node)):
        voltage_now = G.node[j]['voltage'][t] # maybe change to 'G.nodes[]' later
        conductance_E_now = G.node[j]['conductance_E'][t]
        conductance_I_now = G.node[j]['conductance_I'][t]
    # Main Calculations
        summation = 0
        for k in G.neighbors(j):
            if(k != j): #unnecessary unless MultiGraph
                summation = summation + G[j][k]['weight'] * sigma_fn (voltage_now)
        function = (-1 * const._a_I * conductance_I_now + const._a_I * const.conductance_K_max * summation)
        G.node[j]['conductance_I'][t+1] = conductance_I_now + const.dt * function
    return function

def conductance_A_update(G,t):
    """AHP Conductance Update Euler Calculation"""
    # Now Updates:
    for j in range(len(G.node)):
        voltage_now = G.node[j]['voltage'][t] # maybe change to 'G.nodes[]' later
        conductance_E_now = G.node[j]['conductance_E'][t]
        conductance_I_now = G.node[j]['conductance_I'][t]
        conductance_A_now = G.node[j]['conductance_A'][t]
    # Main Calculation
        function = -1 * const._a_A * conductance_A_now + const._a_A * const.w_A * const.conductance_A_max * sigma_fn (voltage_now)
        G.node[j]['conductance_A'][t+1] = conductance_A_now + const.dt * function
    return function

    # Future Work:
    #
    # Find correct values for I, w_A, conductance_A_max
