def timestep_calc (total_time, dt):
    result = int(total_time / dt)
    return result

### Experimental values for constants used in the striatum model

# Inverse Time Constants
_a_E = 1e3     #(sec)^-1
_a_I = 0.2e3   #(sec)^-1
_a_A = 1e3     #(sec)^-1

# Channel Reversing Potentials
voltage_E = 50e-3     #(V) - excitatory
voltage_L = -65e-3   #(V) - leakage
voltage_I = -75e-3   #(V) - inhibitory
voltage_K = -90e-3   #(V) - potassium


# Assorted
conductance_L     = 28e-9    #Siemens - leakage conductance
conductance_K_max = 25e-9    #Siemens - range (0<x<50) change later? Saturation value for K channel
conductance_A_max = 25e-9    #Siemens - Not sure what this should be. Saturation value for AHP channel

capacitance       = 0.5e-9   #F - capacitance of cell membrane
_k                = 8e-1      #(V)^-1 - slope of the sigmoid (smaller is more gradual)
voltage_0         = -45e-3   #(V) -
voltage_thresh    = -50e-3   #(V) - firing threshold
_beta             = 8e-1      #(v)^-1 - tells about slope of sigma (oid?). experiment with value. start out similar to k.
w_A               = 1e-2     # scale factor for AHP
I                 = 1e-3     # striatal afferents determined by cortical afferents (should make dynamic later)
epsilon           = 1e-3     # Constraint on dynamics

tMax              = 10000    # (steps)


# Graph Building

total_time        = 1e-3
dt_list           = []
lowrand           = -1e-3
highrand          = 1e-3

N                 = 2#500  # number of nodes
K                 = 1#7  # average degree
P                 = 1e-5 # 2e-3

# Initial Values
voltage_init            = -70e-3 #volts
conductance_A_init      = 10e-9 #Siemens
conductance_E_init      = 10e-9 #Siemens
conductance_I_init      = 10e-9 #Siemens

### Experimental values for constants used in the LIF model

g_syn                   = 2e-3 # Firing amplitude
I_ext                   = 30e-3#0.85

# Inverse time constants

_a_m                    = 1e3     #(sec)^-1 # inverse of tau_m

# Time constants

_tau_D                  = 1e-4 # (sec) Delay time



# TO DO
# Find initial conductances
#
# Find out why it fires too early (-68mV)
#
# Write out constants in LateX
