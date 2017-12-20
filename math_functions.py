import math
import constants
import numpy as np

#time division is dt

def sigma_fn(voltage_now):
    result = math.pow( 1 + math.exp( _beta * ( voltage_thresh - voltage_now ) ) , -1 ) #figure out what _beta should be
    return result

def sigma_0_fn(voltage_now):
    result = math.pow( 1 + math.exp( _k * ( voltage_0 - voltage_now ) ) , -1 )
    return result


#def v_update_fn(v, dt): #euler update scheme
#    alpha = - (_G_L) / _C # more terms to be added later
#    beta =  ( _V_L * _G_L ) / ( _G_L ) #more terms to be added later
#    result = beta + ( v - beta ) * math.exp( alpha * dt )
#    return result

def voltage_update( G ):

    # Constants List:
    # voltage_E, voltage_I, voltage_L, voltage_K
    # conductance_L, conductance_K_max (variable(?))

    # Now Updates:
    #voltage_now = voltage[j][t]
    #conductance_E_now = conductance_E[j][t]
    #conductance_I_now = conductance_I[j][t]
    #conductance_A_now = conductance_A[j][t]

    voltage_now = G.node[j]['voltage'][t] # maybe change to 'G.nodes[]' later
    conductance_E_now = G.node[j]['conductance_E'][t]
    conductance_I_now = G.node[j]['conductance_I'][t]
    conductance_A_now = G.node[j]['conductance_A'][t]

    # Preliminary calculations:
    excitatory = ( voltage_E - voltage_now ) * conductance_E_now
    inhibitory = ( voltage_I - voltage_now ) * conductance_I_now
    leakage = ( voltage_L - voltage_now ) * conductance_L #this conductance doesn't evolve or depend on neuron
    potassium = ( voltage_K - voltage_now ) * ( conductance_K_max * sigma_0_fn ( voltage_now ) )
    AHP = conductance_A_now

    # Main Calculations:
    G.node[j]['voltage'][t+1] = voltage_now + ( dt / capacitance ) * ( excitatory + leakage + inhibitory + potassium + AHP )

    # Future Work:
    #


def conductance_
