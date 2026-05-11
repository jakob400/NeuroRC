"""F7: Phase 1 behavioural biophysics report.

Runs an STR simulation at the calibrated Poisson defaults (V_thresh =
-42 mV; see BIO-6.2), then measures the three biophysics signatures
that PLAN.md's per-change checks called for:

  - AHP decay tau   (target: ~50 ms; Nisenbaum & Wilson 1995)
  - ISI_5 / ISI_1   (target: >= 1.3; spike-frequency adaptation)
  - IPSC amplitude  (target: 0.5-3 nS; Koos/Tepper/Wilson 2004)

Outputs three numbers to stdout with literature targets. Eyeballable;
not a unit test.

Usage:
    .venv/bin/python scripts/phase1_biophysics_report.py
"""

import numpy as np

import const
from simulate import simulate


def detect_spikes(V_trace, V_reset=None):
    """Return indices where V crosses into V_reset (a spike just fired)."""
    if V_reset is None:
        V_reset = const.V_reset
    above = V_trace[:-1] > V_reset + 1e-9
    reset = V_trace[1:] <= V_reset + 1e-9
    return np.flatnonzero(above & reset) + 1


def ahp_tau(g_A_trace, spike_idx, dt, min_isi_steps=4000):
    """Fit g_A(t) = baseline + (peak - baseline) * exp(-t / tau) on the
    post-spike decay of a spike that has no follow-up spike for at least
    min_isi_steps (100 ms at dt=25us). Baseline is estimated as the
    minimum of the last 10% of the decay window."""
    n_steps = g_A_trace.shape[0]
    spk = np.asarray(spike_idx)
    for i, s in enumerate(spk):
        next_s = spk[i + 1] if i + 1 < len(spk) else n_steps
        gap = next_s - s
        if gap < min_isi_steps:
            continue
        end = min(s + min_isi_steps, n_steps)
        seg = g_A_trace[s + 1:end]
        if len(seg) < 200:
            continue
        peak = float(seg[0])
        tail = seg[int(0.8 * len(seg)):]
        baseline = float(tail.mean())
        amplitude = peak - baseline
        if amplitude < 1e-12:
            continue
        # Fit log(seg - baseline) vs t.
        adj = seg - baseline
        mask = adj > 0.1 * amplitude
        if mask.sum() < 50:
            continue
        ts = np.arange(seg.shape[0])[mask] * dt
        ys = np.log(adj[mask])
        slope, _ = np.polyfit(ts, ys, 1)
        if slope >= 0:
            continue
        return -1.0 / slope, peak, int(s)
    return None, None, None


def isi_ratio(spike_idx, dt):
    """Return ISI_5 / ISI_1 if at least 6 spikes; else None."""
    if len(spike_idx) < 6:
        return None
    isis = np.diff(spike_idx) * dt
    return isis[4] / isis[0]


def main():
    print('STR biophysics report (Phase 1 BIO-1/2/3 sanity)')
    print('V_thresh = %.1f mV, poisson_rate = %.1f kHz, delta_g_E = %.2f nS'
          % (const.V_thresh * 1000, const.poisson_rate / 1e3,
             const.poisson_delta_g_E * 1e9))

    # Larger network and longer run give enough spikes for ISI stats and
    # at least one isolated post-spike window for the AHP fit.
    N, tMax = 200, 100000
    G, state = simulate('STR', N=N, K=20, P=0.1, tMax=tMax, seed=0,
                        fixed_dt_mode=True)
    dt = const.dt_fixed
    V = np.asarray(state.history['V'])
    g_A = np.asarray(state.history['g_A'])
    g_I = np.asarray(state.history['g_I'])

    sim_s = V.shape[0] * dt
    total_spikes = sum(len(detect_spikes(V[:, j])) for j in range(N))
    print()
    print('Simulated %.3f s on N=%d, K=20, P=0.1' % (sim_s, N))
    print('Total spikes: %d (%.3f Hz/neuron)' % (total_spikes,
                                                  total_spikes / N / sim_s))

    # AHP decay: scan all neurons for one with a >200 ms isolated post-spike
    # window. Aggregate tau across qualifying fits.
    print()
    print('--- AHP decay (BIO-1, target tau ~ 50 ms)')
    fits = []
    for j in range(N):
        s_j = detect_spikes(V[:, j])
        if len(s_j) < 1:
            continue
        tau, peak, s_idx = ahp_tau(g_A[:, j], s_j, dt)
        if tau is not None:
            fits.append((j, tau, peak, s_idx))
    if not fits:
        print('  no neuron with a clean isolated post-spike window')
    else:
        taus = np.array([f[1] for f in fits])
        print('  %d clean fits; tau = %.1f +- %.1f ms (median %.1f ms)'
              % (len(fits), taus.mean() * 1000, taus.std() * 1000,
                 float(np.median(taus)) * 1000))

    # ISI ratio: prefer a neuron with at least 6 spikes; report mean across
    # all such neurons.
    print()
    print('--- ISI_5 / ISI_1 (BIO-2, target >= 1.3)')
    ratios = []
    for j in range(N):
        s_j = detect_spikes(V[:, j])
        r = isi_ratio(s_j, dt)
        if r is not None:
            ratios.append(r)
    if not ratios:
        print('  no neuron with >= 6 spikes')
    else:
        ratios = np.asarray(ratios)
        print('  %d neurons qualified; ISI_5/ISI_1 = %.2f +- %.2f (median %.2f)'
              % (len(ratios), float(ratios.mean()), float(ratios.std()),
                 float(np.median(ratios))))

    # IPSC scale: g_I peaks across all neurons indicate magnitude of
    # recurrent inhibitory PSCs. The model's unitary IPSC size is
    # const.conductance_I_max (set by BIO-3 to 1.5 nS).
    g_I_peak = float(g_I.max())
    g_I_mean = float(g_I.mean())
    print()
    print('--- IPSC scale (BIO-3, target 0.5-3 nS unitary)')
    print('  g_I_max parameter = %.2f nS' % (const.conductance_I_max * 1e9))
    print('  observed g_I:  mean = %.2f nS, peak = %.2f nS'
          % (g_I_mean * 1e9, g_I_peak * 1e9))


if __name__ == '__main__':
    main()
