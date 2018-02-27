import math
import numpy as np
import const
import networkx as nx
import random


def get_Rand():
    state = get_Sign() * round(np.random.normal(0,5e-5), int(random.uniform(10,15)))
    return state

def get_Sign():
    value = round(random.uniform(0,1))
    if (value==0):
        state = -1
    else:
        state = 1
    return state
#time division is dt

def sigma(voltage_now):
    """ Regular sigma calculation """
    result = math.pow(1 + math.exp(const._beta * (const.voltage_thresh - voltage_now)), -1) #figure out what _beta should be
    return result

def sigma_0(voltage_now):
    """ Sigma_0 calculation """
    result = math.pow(1 + math.exp(const._k * (const.voltage_0 - voltage_now)), -1)
    return result

def delta(neighbor_voltages,t):
    """ Checks if there has been a pulse _tau_D seconds ago and responds accordingly """
    t_delayed = delay(t)
    summation = 0
    for i in range(len(neighbor_voltages)):
        summation += neighbor_voltages[t_delayed]
    return summation

def delay(t):
    """ Calculates how many timesteps ago _tau_D is  """
    dt_sum = 0
    i = 0
    while( dt_sum < const._tau_D ):
        if(len(const.dt_list) > i): # Does not proceed if list of dt's is not long enough.
            dt_sum += const.dt_list[-i-1]
            i += 1
        else:
            break
    print('dt_sum is',dt_sum)
    print('_tau_D is',const._tau_D)
    print('steps back is',i)
    print('time_delayed is ', t-i,'\n')
    return t-i







    # Future Work:
    #
    # Find correct values for I, w_A, conductance_A_max
    #
    # Add in conductance_I_max
