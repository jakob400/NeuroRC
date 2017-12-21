#Experimental values for constants used in the striatum model

#Inverse Time Constants
_a_E = 1     #(msec)^-1
_a_I = 0.2   #(msec)^-1
_a_A = 1     #(msec)^-1


#Channel Reversing Potentials
voltage_E = 0     #(mV) - excitatory
voltage_L = -65   #(mV) - leakage
voltage_I = -75   #(mV) - inhibitory
voltage_K = -90   #(mV) - potassium


#Assorted
conductance_L     = 28    #nS - leakage conductance
conductance_K_max = 25    #nS - range (0<x<50) change later?

capacitance       = 0.5   #nF - capacitance of cell membrane
_k                = 0.08  #(mV)^-1 - slope of the sigmoid (smaller is more gradual)
voltage_0         = -45   #(mV) -
voltage_thresh    = -50   #(mV) - firing threshold
_beta             = 0.08  #(mv)^-1 - tells about slope of sigma (oid?). experiment with value. start out similar to k.
dt                = 100   # msec (time increment)
