import math
import const
import networkx as nx
import random

def get_Rand():
    state = get_Sign() * round(random.uniform(const.lowrand,const.highrand), int(random.uniform(10,15)))
    return state

def get_Sign():
    value = round(random.uniform(0,1))
    if (value==0):
        state = -1
    else:
        state = 1
    return state
#time division is dt

def sigma_fn(voltage_now):
    """ Regular sigma calculation """
    result = math.pow(1 + math.exp(const._beta * (const.voltage_thresh - voltage_now)), -1) #figure out what _beta should be
    return result

def sigma_0_fn(voltage_now):
    """ Sigma_0 calculation """
    result = math.pow(1 + math.exp(const._k * (const.voltage_0 - voltage_now)), -1)
    return result


def update_state(G,t):
    """ Master Update Calculation """
    print('\r', t,end='')
    for j in range(len(G.node)): # for loop over all nodes in G
    # Initializations:
        func_v = [None] * len(G.node)
        func_A = [None] * len(G.node)
        func_E = [None] * len(G.node)
        func_I = [None] * len(G.node)

    # Now Updates:
        voltage_now = G.node[j]['voltage'][t] # maybe change to 'G.nodes[]' later
        conductance_E_now = G.node[j]['conductance_E'][t]
        conductance_I_now = G.node[j]['conductance_I'][t]
        conductance_A_now = G.node[j]['conductance_A'][t]

    # Preliminary Voltage calculations:
        excitatory = (const.voltage_E - voltage_now) * conductance_E_now
        inhibitory = (const.voltage_I - voltage_now) * conductance_I_now
        leakage = (const.voltage_L - voltage_now) * const.conductance_L #this conductance doesn't evolve or depend on neuron
        potassium = (const.voltage_K - voltage_now) * (const.conductance_K_max * sigma_0_fn(voltage_now) + conductance_A_now)

    # Func Calculations:
        func_v[j] = ( 1 / const.capacitance) * (excitatory + leakage + inhibitory + potassium ) #potassium includes AHP, due to equation
        func_E[j] = (-1 * const._a_E * conductance_E_now + const.I)
        func_A[j] = -1 * const._a_A * conductance_A_now + const._a_A * const.w_A * const.conductance_A_max * sigma_fn (voltage_now)
        summation = 0
        for k in G.neighbors(j):
            if(k != j): # Redundant unless MultiGraph
                neighbor_voltage = G.node[k]['voltage'][t]
                summation = summation + G[j][k]['weight'] * sigma_fn (neighbor_voltage)
        func_I[j] = (-1 * const._a_I * conductance_I_now + const._a_I * const.conductance_K_max * summation)

    # Randomness Generator
        func_v[j] = func_v[j] + get_Rand()
        func_E[j] = func_E[j] + get_Rand()
        func_A[j] = func_A[j] + get_Rand()
        func_I[j] = func_I[j] + get_Rand()

    # Dynamic Protection:
        M = max(func_v[j],func_E[j],func_I[j],func_A[j])

    # Main Calculations
        if (func_v[j] < (const.epsilon * M)):
            G.node[j]['voltage'][t+1] = voltage_now + const.dt * func_v[j]
        if (func_E[j] < (const.epsilon * M)):
            G.node[j]['conductance_E'][t+1] = conductance_E_now + const.dt * func_E[j]
        if (func_I[j] < (const.epsilon * M)):
            G.node[j]['conductance_I'][t+1] = conductance_I_now + const.dt * func_I[j]
        if (func_A[j] < (const.epsilon * M)):
            G.node[j]['conductance_A'][t+1] = conductance_A_now + const.dt * func_A[j]
    return G


    # Future Work:
    #
    # Find correct values for I, w_A, conductance_A_max
    #
    # Correct issue where only last function would be returned
    #
    # Maybe change order of calculations.
    #
    # Everything seems uncoupled. Look into this.
