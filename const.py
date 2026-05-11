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

# Slow K inward rectifier (Kir2 / persistent K) for up-down state bistability.
# Active near rest, rectifies (closes) as V depolarizes. Combined with a slow
# activation time constant, gives the regenerative bistability that lets MSNs
# sit in a -75 mV "down state" most of the time and intermittently transition
# to a -55 mV "up state" where they fire 1-5 spikes. Biology: Wilson &
# Kawaguchi 1996 (J Neurosci 16:2397); Mahon et al. 2006 (J Neurosci 26:12587);
# Nisenbaum & Wilson 1995 (J Neurosci 15:4449). Parameters tuned empirically
# against scripts/diag_alpha_beta_grid.py feasibility.
conductance_KIR_max = 15e-9  #Siemens - slow K saturation
voltage_KIR_half    = -60e-3 #(V) - half-activation; midpoint between down and up states
_k_KIR              = 200    #(V)^-1 - slope of sigma_KIR; ~14 mV transition width
_a_KIR              = 5.0    #(sec)^-1 - inverse time constant; tau_KIR = 200 ms

capacitance       = 0.5e-9   #F - capacitance of cell membrane
_k                = 250      #(V)^-1 - slope of sigma_0 (Ponzi-Wickens 2010); transition width ~17 mV
voltage_0         = -45e-3   #(V) -
voltage_thresh    = -50e-3   #(V) - half-activation voltage for sigma_0 (not the spike threshold)

# Spike-reset policy (BIO-7): integrate-and-fire with a hard threshold.
# When V crosses V_thresh, V is set to V_reset and held there for t_refr.
# -41 mV: D1 recalibration. GRAPH-3's directed-adjacency fix halved the
# recurrent inhibition density that the prior -42 mV setting was tuned
# against, pushing the network to 18 Hz/neuron. scripts/diag_recalibrate_
# directed.py sweeps V_thresh and confirms -41 mV restores the 0.5-2
# Hz/neuron physiological MSN regime (literature window: Wilson &
# Kawaguchi 1996; Mahon 2006). See DIAGNOSTICS.md D1/D4.
V_thresh          = -41e-3   #(V) - spike threshold
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

# Adaptive Euler safety clamps. At equilibrium f(V) -> 0, so epsilon/max|f|
# diverges and a single step can leap simulated time by years. dt_max bounds
# that; dt_floor prevents an enormous spike-rise burst from collapsing dt
# below numerical resolution. Active only when fixed_dt_mode=False.
dt_floor          = 1e-9     # (s)
dt_max            = 1e-3     # (s)


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

# Lognormal weight calibration for the Koos 2004 striatal MSN-MSN IPSC
# (GRAPH-1). Per-synapse mean = 500 pS, CV = 1.0. With these in Siemens,
# the recurrent inhibitory product conductance_I_max * weight reads as
# (1.5 nS) * (500 pS) which is too small by ~3 orders of magnitude; callers
# selecting lognormal weights should either drop conductance_I_max to 1.0
# or interpret weights as dimensionless multipliers (mean ~1) by setting
# mean_S=1.0 explicitly via assign_weights kwargs.
R_in              = 200e6    # Ohm, MSN input resistance (Plenz & Aertsen 1996)
weight_mean_S     = 0.5e-9   # S, mean unitary g_syn (Koos 2004)
weight_cv         = 1.0

# Initial Values
voltage_init            = -70e-3 #volts
conductance_A_init      = 10e-9 #Siemens
conductance_E_init      = 10e-9 #Siemens
conductance_I_init      = 10e-9 #Siemens
# Initial g_KIR. At V_init = -70 mV, sigma_KIR ~ 0.88, so the steady-state
# initial value is conductance_KIR_max * 0.88 ~ 13 nS. Set explicitly so the
# network starts in the down state.
conductance_KIR_init    = 13e-9 #Siemens

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
