def timestep_calc (total_time, dt):
    result = int(total_time / dt)
    return result

### Experimental values for constants used in the striatum model

# Inverse Time Constants
_a_E = 1e3     #(sec)^-1
_a_I = 0.2e3   #(sec)^-1
_a_A = 20      #(sec)^-1 - tau_AHP = 50 ms (Nisenbaum & Wilson 1995)

# Channel Reversing Potentials
voltage_E = 50e-3     #(V) - excitatory
voltage_L = -65e-3   #(V) - leakage
voltage_I = -75e-3   #(V) - inhibitory
voltage_K = -90e-3   #(V) - potassium


# Assorted
conductance_L     = 28e-9    #Siemens - leakage conductance
conductance_K_max = 25e-9    #Siemens - voltage-gated K saturation (drives potassium term via sigma_0)
conductance_A_max = 25e-9    #Siemens - AHP channel saturation
conductance_I_max = 1.5e-9   #Siemens - unitary recurrent IPSC scale (Koos/Tepper/Wilson 2004)

capacitance       = 0.5e-9   #F - capacitance of cell membrane
_k                = 250      #(V)^-1 - slope of sigma_0 (Ponzi-Wickens 2010); transition width ~17 mV
voltage_0         = -45e-3   #(V) -
voltage_thresh    = -50e-3   #(V) - half-activation voltage for sigma_0 (not the spike threshold)

# Spike-reset policy (BIO-7): integrate-and-fire with a hard threshold.
# When V crosses V_thresh, V is set to V_reset and held there for t_refr.
V_thresh          = -40e-3   #(V) - spike threshold
V_reset           = -70e-3   #(V) - post-spike voltage
t_refr            = 2e-3     #(s) - absolute refractory period
_beta             = 250      #(V)^-1 - slope of sigma (Ponzi-Wickens 2010); matched to _k for STR threshold gating
w_A               = 0.5      # scale factor for AHP - lifted from 0.01 so adaptation reaches ~1% of leak current at saturation (Ponzi-Wickens 2010)
I                 = 1e-3     # constant cortical drive (used only when drive_mode == 'constant')

# Cortical drive: 'constant' keeps the legacy +I term in func_E; 'poisson'
# drops it and instead delivers Poisson-distributed excitatory kicks of size
# poisson_delta_g_E at rate poisson_rate (per neuron). Poisson drive is
# required for decorrelation / reservoir / assembly analyses.
drive_mode        = 'poisson'
# Aggregate cortical Poisson drive per MSN: rate * delta_g_E / _a_E sets g_E
# steady state. Calibrated to deliver V_ss near V_thresh so the network fires
# at ~0.5-2 Hz/neuron in line with in vivo MSN rates (Mahon 2006, Sippy 2015).
# Fine biophysical calibration (per-synapse delta_g_E, kAMPA tau) is deferred.
poisson_rate      = 2.0e4    # Hz (aggregate)
poisson_delta_g_E = 1.0e-9   # S (1 nS per kick, aggregate)
epsilon           = 1e-3     # Constraint on dynamics

tMax              = 10000    # (steps)

# Integrator selection (NUM-3): True uses fixed-dt Heun on V + exp-Euler on
# conductances at dt_fixed. False uses the legacy adaptive Euler stepper.
fixed_dt_mode     = True
dt_fixed          = 25e-6    # (s) - 25 us; bracketed by spike-rise time and AMPA tau


# Graph Building

total_time        = 1e-3
lowrand           = -1e-3
highrand          = 1e-3

N                 = 2#500  # number of nodes
K                 = 1#7  # average degree
P                 = 1e-5 # 2e-3

# Synaptic weight distribution (uniform). O(1) weights yield mV-scale LIF
# inputs (g_syn ~ 2e-3) and ~nS recurrent inhibitory drive in STR
# (a_I * conductance_K_max * weight * sigma). Calibrated further in Phase 1.
weight_low        = 0.0
weight_high       = 1.0

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
