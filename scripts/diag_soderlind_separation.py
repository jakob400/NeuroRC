"""Diagnostic: does S(t) = log(1/dt(t)) carry smooth-dynamics info
beyond spike-event marking?

The Soderlind/Jay/Calvo 2015 theorem says S(t) approximates the local
logarithmic norm mu(J(t)) of the Jacobian when ODE dynamics are
approximately linear in the direction of fastest motion. That's true
between spikes (smooth LIF/STR ODE). It's NOT obviously true at spike-
reset events, which are discrete jumps that the ODE-stiffness story
does not cover.

For Proposal #2 the publishable claim is that S(t) detects state
transitions. The folklore objection: dt drops near spikes, of course,
because the controller backs off. To distinguish these we ask:

  Is the *between-spike* dt sequence informative on its own?

If yes, S(t) carries genuine Soderlind-style smooth-dynamics info
beyond the spike marker -- the publishable claim survives.
If no, S(t) is dominated by spike-marking -- the folklore objection
sticks and Proposal #2 dies at peer review.

Protocol:
  1. Run LIF in sub-threshold regime (I_ext too small to ever fire):
     measure the dt distribution. Here there are *no* spike events;
     every step is pure ODE evolution.
  2. Run LIF in supra-threshold regime (default I_ext):
     separate dts into 'within refractory' vs 'in active firing'.
  3. Compare the between-spike supra-threshold dts to the sub-threshold
     baseline. If they agree, S(t) between spikes IS the Soderlind
     signal.
"""

import numpy as np

import const
from simulate import simulate


def run_lif(I_ext, tMax, N=50, K=4, P=0.05, seed=0):
    saved = const.I_ext
    const.I_ext = I_ext
    try:
        G, s = simulate('LIF', N=N, K=K, P=P, tMax=tMax,
                        seed=seed, fixed_dt_mode=False)
    finally:
        const.I_ext = saved
    return s


def spike_steps(V):
    above = V[:-1] > const.V_reset + 1e-9
    reset = V[1:] <= const.V_reset + 1e-9
    return np.any(above & reset, axis=1)


def step_in_refractory(state):
    """Mask: True if at step t any neuron is within the refractory window.

    Approximated using the time since each neuron's last_spike_time;
    a step is 'in refractory' if at least one neuron is refractory.
    We use the cumulative time at each step.
    """
    V = np.asarray(state.history['V'])
    n_steps = V.shape[0]
    if not state.dt_list:
        return np.zeros(n_steps, dtype=bool)
    t_axis = np.concatenate(([0.0], np.cumsum(state.dt_list)))[:n_steps]
    # Reconstruct spike events per step:
    above = V[:-1] > const.V_reset + 1e-9
    reset = V[1:] <= const.V_reset + 1e-9
    spike_step = above & reset  # (n_steps-1, N)
    # For each step, time since *any* neuron last spiked
    last_t = np.full(V.shape[1], -np.inf)
    in_refr = np.zeros(n_steps, dtype=bool)
    for i in range(spike_step.shape[0]):
        for j in np.flatnonzero(spike_step[i]):
            last_t[j] = t_axis[i + 1]
        if np.any(t_axis[i + 1] - last_t < const.t_refr):
            in_refr[i + 1] = True
    return in_refr


def summarize(name, dts):
    if len(dts) == 0:
        print('  %-30s n=0' % name)
        return
    print('  %-30s n=%5d  median=%.3g  p10=%.3g  p90=%.3g  mean=%.3g'
          % (name, len(dts),
             float(np.median(dts)),
             float(np.percentile(dts, 10)),
             float(np.percentile(dts, 90)),
             float(np.mean(dts))))


def main():
    print('=== Soderlind separability diagnostic ===')

    # I_ext below V_thresh = -42 mV so V equilibrates below threshold and
    # spikes are mathematically impossible.
    print('\n--- Regime A: sub-threshold (no spikes possible) ---')
    s_sub = run_lif(I_ext=-50e-3, tMax=10000)
    # Confirm no spikes in this regime
    V_sub = np.asarray(s_sub.history['V'])
    n_spikes_sub = ((V_sub[:-1] > const.V_reset + 1e-9)
                    & (V_sub[1:] <= const.V_reset + 1e-9)).sum()
    print('Confirm 0 spikes: actually %d' % n_spikes_sub)
    dts_sub = np.asarray(s_sub.dt_list)
    sim_s = float(dts_sub.sum())
    print('Sim time: %.4f s; mean dt: %.3g; max dt: %.3g'
          % (sim_s, dts_sub.mean(), dts_sub.max()))
    summarize('all dt (sub-threshold)', dts_sub)

    print('\n--- Regime B: supra-threshold (firing) ---')
    s_sup = run_lif(I_ext=30e-3, tMax=10000)
    V_sup = np.asarray(s_sup.history['V'])
    n_spikes_sup = ((V_sup[:-1] > const.V_reset + 1e-9)
                    & (V_sup[1:] <= const.V_reset + 1e-9)).sum()
    print('Spike events: %d' % n_spikes_sup)
    dts_sup = np.asarray(s_sup.dt_list)
    print('Sim time: %.4f s; mean dt: %.3g'
          % (dts_sup.sum(), dts_sup.mean()))

    # Steps where at least one neuron is in refractory
    in_refr = step_in_refractory(s_sup)
    in_refr = in_refr[:dts_sup.shape[0]]
    dts_refr = dts_sup[in_refr]
    dts_active = dts_sup[~in_refr]
    summarize('all dt (supra-threshold)', dts_sup)
    summarize('dt during refractory',  dts_refr)
    summarize('dt during active dynamics', dts_active)

    print('\n--- Decisive comparison ---')
    print('Sub-threshold dt vs supra-threshold active-dynamics dt:')
    summarize('sub-threshold all',  dts_sub)
    summarize('supra active',       dts_active)

    # The decisive question: does S(t) = log(1/dt) carry usable signal?
    # If log(dt) is essentially constant across all regimes, then S(t)
    # carries no information regardless of whether the Soderlind theorem
    # applies in principle.
    log_sub = np.log(np.maximum(dts_sub, 1e-12))
    log_sup_all = np.log(np.maximum(dts_sup, 1e-12))
    log_sup_active = np.log(np.maximum(dts_active, 1e-12))
    log_sup_refr = np.log(np.maximum(dts_refr, 1e-12))
    print()
    print('Absolute log(dt) variability (= raw S(t) signal range):')
    print('  sub-threshold:   median=%7.3f  std=%6.3f  p5..p95=[%7.3f, %7.3f]' %
          (float(np.median(log_sub)), float(np.std(log_sub)),
           float(np.percentile(log_sub, 5)),
           float(np.percentile(log_sub, 95))))
    if len(log_sup_refr) > 0:
        print('  supra refractory:median=%7.3f  std=%6.3f  p5..p95=[%7.3f, %7.3f]' %
              (float(np.median(log_sup_refr)), float(np.std(log_sup_refr)),
               float(np.percentile(log_sup_refr, 5)),
               float(np.percentile(log_sup_refr, 95))))
    if len(log_sup_active) > 0:
        print('  supra active:    median=%7.3f  std=%6.3f  p5..p95=[%7.3f, %7.3f]' %
              (float(np.median(log_sup_active)), float(np.std(log_sup_active)),
               float(np.percentile(log_sup_active, 5)),
               float(np.percentile(log_sup_active, 95))))

    # Variability budget
    total_log_range = float(log_sup_all.max() - log_sup_all.min())
    print()
    print('Total log(1/dt) range across the supra-threshold run: %.3f' %
          total_log_range)
    print('(Equivalent to dt varying by a factor of %.3g)' %
          np.exp(total_log_range))

    # Also check STR: its 4 state variables and Poisson kicks to g_E
    # might give wider ||f|| variation than LIF.
    print('\n--- STR check: same diagnostic on the conductance-based model ---')
    saved_dtmode = const.fixed_dt_mode
    const.fixed_dt_mode = False
    try:
        G_str, s_str = simulate('STR', N=50, K=4, P=0.05, tMax=10000,
                                seed=0, fixed_dt_mode=False)
    finally:
        const.fixed_dt_mode = saved_dtmode
    dts_str = np.asarray(s_str.dt_list)
    log_str = np.log(np.maximum(dts_str, 1e-12))
    print('STR sim time: %.4f s; n_steps=%d' % (dts_str.sum(), len(dts_str)))
    print('STR log(dt): median=%.3f std=%.3f p5..p95=[%.3f, %.3f]'
          % (float(np.median(log_str)), float(np.std(log_str)),
             float(np.percentile(log_str, 5)),
             float(np.percentile(log_str, 95))))
    str_range = float(log_str.max() - log_str.min())
    print('STR total log(1/dt) range: %.3f (dt varies by factor %.3g)'
          % (str_range, np.exp(str_range)))

    if total_log_range < 1.0:
        verdict = ('S(t) varies by less than a factor of e across the run. '
                   'Z-scoring this signal would inflate pure numerical '
                   'jitter into apparent structure. Proposal #2 in '
                   'serious trouble.')
    elif total_log_range < 3.0:
        verdict = 'S(t) varies modestly. Detector usefulness uncertain.'
    else:
        verdict = ('S(t) shows multi-order-of-magnitude variation. The '
                   'Soderlind-applicability question is still open but '
                   'the signal at least has structure to work with.')
    print('\nVerdict: ' + verdict)


if __name__ == '__main__':
    main()
