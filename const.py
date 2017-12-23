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
conductance_K_max = 25e-9    #Sieverts - range (0<x<50) change later? Saturation value for K channel
conductance_A_max = 25e-9    #Sieverts - Not sure what this should be. Saturation value for K channel

capacitance       = 0.5e-9   #F - capacitance of cell membrane
_k                = 0.08e3   #(V)^-1 - slope of the sigmoid (smaller is more gradual)
voltage_0         = -45e-3   #(V) -
voltage_thresh    = -50e-3   #(V) - firing threshold
_beta             = 0.08e3   #(v)^-1 - tells about slope of sigma (oid?). experiment with value. start out similar to k.
w_A               = 1e-2        # scale factor for AHP
I                 = 1e-2        # striatal afferents determined by cortical afferents (should make dynamic later)
epsilon           = 1     # Constraint on dynamics


# Graph Building
timesteps         = 50
dt                = 1e-4      # sec (time increment)

N                 = 1000  # number of nodes
K                 = 7  # average degree
P                 = 1#1e-5#2e-3

# Initial Values
voltage_init            = -70e-3 #volts
conductance_A_init      = 0 #Sieverts
conductance_E_init      = 0 #Sieverts
conductance_I_init      = 0 #Sieverts
