# Experimental values for constants used in the striatum model

# Inverse Time Constants
_a_E = 1e3     #(sec)^-1
_a_I = 0.2e3   #(sec)^-1
_a_A = 1e3     #(sec)^-1


# Channel Reversing Potentials
voltage_E = 0e-3     #(V) - excitatory
voltage_L = -65e-3   #(V) - leakage
voltage_I = -75e-3   #(V) - inhibitory
voltage_K = -90e-3   #(V) - potassium


# Assorted
conductance_L     = 28e-9    #Sieverts - leakage conductance
conductance_K_max = 25e-9    #Sieverts - range (0<x<50) change later?

capacitance       = 0.5e-9   #F - capacitance of cell membrane
_k                = 0.08e3   #(V)^-1 - slope of the sigmoid (smaller is more gradual)
voltage_0         = -45e-3   #(V) -
voltage_thresh    = -50e-3   #(V) - firing threshold
_beta             = 0.08e3   #(v)^-1 - tells about slope of sigma (oid?). experiment with value. start out similar to k.

I                 = 1e-6 #no clue what this is


# Graph Building
timesteps         = 10
dt                = 7e-3      # sec (time increment)
N                 = 250  # number of nodes
K                 = 230  # average degree
P                 = 5 * 10e-2
