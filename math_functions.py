import math
import constants
import numpy as np

def sigma_fn(v):
    result = math.pow( 1 + math.exp( _beta * ( _V_T - v) ) , -1 ) #figure out what _beta should be
    return result

def sigma_0_fn(v):
    result = math.pow( 1 + math.exp( _k * ( _V_0 - v) ) , -1 )
    return result


#def v_update_fn(v, dt): #euler update scheme
#    alpha = - (_G_L) / _C # more terms to be added later
#    beta =  ( _V_L * _G_L ) / ( _G_L ) #more terms to be added later
#    result = beta + ( v - beta ) * math.exp( alpha * dt )
#    return result
