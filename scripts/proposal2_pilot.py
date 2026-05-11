"""Proposal #2 pilot: K-sweep on NWS DiGraph for synchronization onset.

Falsification criterion from RESEARCH_DIRECTIONS.md:
    S(t) must beat *both* sigma^2_r and AC(1) in mean lead-time at 5%
    FPR by >= 20 ms (Wilcoxon p < 0.05).

This script is the scaffold. It runs a reduced sweep (fewer K-values,
fewer seeds) than the full 50 x 30 pilot so the artifact is testable
locally. The reduced run can be scaled up by editing the K_VALUES /
N_SEEDS_PER_K constants.

Usage:
    uv run python -m scripts.proposal2_pilot

Output:
    logs/proposal2_pilot_results.npz containing per-(K, seed):
        - kuramoto_R: time-series of order parameter
        - transition_step: oracle first-crossing index (or -1)
        - lead_time_S, lead_time_sigma2, lead_time_ac1, lead_time_Hspec
"""

import os
import time

import numpy as np

import const
from simulate import simulate
from metrics import ews, oracles, stats


# Reduced from the full 50 x 30 pilot for local tractability.
K_VALUES = [2, 4, 8, 16, 32]
N_SEEDS_PER_K = 3
N_NODES = 200
P_NWS = 0.05
T_MAX_STEPS = 100000
DT_TARGET_MS = 0.5
KURAMOTO_THRESHOLD = 0.5
MIN_DWELL_MS = 50.0
LABEL_HORIZON_MS = 100.0


def randomize_V(rng):
    """Closure returning a state_init callable that scatters V uniformly
    over (V_reset, V_thresh) so the network starts desynchronized."""
    def init(state):
        state.V[:] = rng.uniform(const.V_reset + 0.001,
                                 const.V_thresh - 0.001,
                                 size=state.N)
        state.V_buffer.push(state.V.copy())
        state.history['V'][0] = state.V.copy()
    return init


def run_one(K, seed):
    rng_init = np.random.default_rng(seed * 977 + 17)
    G, s = simulate('LIF', N=N_NODES, K=K, P=P_NWS, tMax=T_MAX_STEPS,
                    seed=seed, fixed_dt_mode=False,
                    state_init=randomize_V(rng_init))

    dts = np.asarray(s.dt_list)
    V_hist = np.asarray(s.history['V'])
    t_uniform, V_uniform = ews.resample_uniform(V_hist, dts,
                                                dt_target_ms=DT_TARGET_MS)
    if V_uniform.shape[0] < 100:
        return None

    R = oracles.kuramoto_order(V_uniform, dt=DT_TARGET_MS * 1e-3)
    transition = oracles.first_crossing(
        R, threshold=KURAMOTO_THRESHOLD,
        min_dwell_steps=int(MIN_DWELL_MS / DT_TARGET_MS))

    r = ews.population_rate(V_uniform, dt=DT_TARGET_MS * 1e-3,
                            V_reset=const.V_reset, bin_ms=1.0)
    sigma2 = ews.rolling_variance(r, dt_ms=1.0)
    ac1 = ews.rolling_ac1(r, dt_ms=1.0)
    H_spec = ews.rolling_spectral_entropy(r, dt_ms=1.0)
    _, S = ews.S_from_dt(dts, dt_target_ms=DT_TARGET_MS,
                        lowpass_hz=100.0, zscore_window_ms=200.0)

    # Map the Kuramoto-grid transition step to each detector's own grid.
    if transition < 0:
        lts = {'S': float('nan'), 'sigma2': float('nan'),
               'ac1': float('nan'), 'Hspec': float('nan')}
    else:
        # R is on the resampled (dt_target_ms) grid; convert to seconds.
        transition_s = transition * DT_TARGET_MS * 1e-3
        # rolling detectors step every 10 ms; S(t) is on dt_target_ms grid.
        step_s_rolling = 10.0 * 1e-3
        step_s_S = DT_TARGET_MS * 1e-3
        lts = {
            'sigma2': stats.lead_time_at_fpr(
                sigma2, int(transition_s / step_s_rolling)),
            'ac1': stats.lead_time_at_fpr(
                ac1, int(transition_s / step_s_rolling)),
            'Hspec': stats.lead_time_at_fpr(
                H_spec, int(transition_s / step_s_rolling)),
            'S': stats.lead_time_at_fpr(
                S, int(transition_s / step_s_S)),
        }

    return {
        'K': K, 'seed': seed,
        'sim_seconds': float(sum(dts)),
        'transition_step_R': int(transition),
        'mean_R': float(R.mean()),
        'max_R': float(R.max()),
        'lead_time_S': lts['S'],
        'lead_time_sigma2': lts['sigma2'],
        'lead_time_ac1': lts['ac1'],
        'lead_time_Hspec': lts['Hspec'],
    }


def main():
    os.makedirs('logs', exist_ok=True)
    print('=== Proposal #2 K-sweep pilot ===')
    print('K_VALUES=%s, seeds per K=%d, N=%d, P=%.3g, tMax=%d steps'
          % (K_VALUES, N_SEEDS_PER_K, N_NODES, P_NWS, T_MAX_STEPS))

    results = []
    t0 = time.perf_counter()
    for K in K_VALUES:
        for seed in range(N_SEEDS_PER_K):
            t1 = time.perf_counter()
            r = run_one(K, seed)
            if r is None:
                print('  K=%2d seed=%d -> too few sim steps, skipped'
                      % (K, seed))
                continue
            print('  K=%2d seed=%d  sim=%.2fs wall=%.2fs '
                  'R_max=%.3f trans=%4d  '
                  'LT(S/sigma2/AC1/H)=%6.1f/%6.1f/%6.1f/%6.1f' % (
                      K, seed, r['sim_seconds'],
                      time.perf_counter() - t1,
                      r['max_R'], r['transition_step_R'],
                      r['lead_time_S'], r['lead_time_sigma2'],
                      r['lead_time_ac1'], r['lead_time_Hspec']))
            results.append(r)

    if not results:
        print('  no successful runs; abort')
        return

    out_path = 'logs/proposal2_pilot_results.npz'
    np.savez(out_path,
             K=np.array([r['K'] for r in results]),
             seed=np.array([r['seed'] for r in results]),
             lead_time_S=np.array([r['lead_time_S'] for r in results]),
             lead_time_sigma2=np.array([r['lead_time_sigma2']
                                         for r in results]),
             lead_time_ac1=np.array([r['lead_time_ac1']
                                      for r in results]),
             lead_time_Hspec=np.array([r['lead_time_Hspec']
                                        for r in results]),
             transition_step=np.array([r['transition_step_R']
                                        for r in results]),
             max_R=np.array([r['max_R'] for r in results]))
    print('\nSaved %d rows to %s' % (len(results), out_path))

    # Compare S(t) vs each baseline via paired Wilcoxon.
    lt_S = np.array([r['lead_time_S'] for r in results])
    lt_sigma2 = np.array([r['lead_time_sigma2'] for r in results])
    lt_ac1 = np.array([r['lead_time_ac1'] for r in results])
    print('\nPaired Wilcoxon (S vs baseline):')
    for name, lt_base in [('sigma^2', lt_sigma2), ('AC(1)', lt_ac1)]:
        stat, p = stats.wilcoxon_compare(lt_S, lt_base)
        sm, bm = float(np.nanmean(lt_S)), float(np.nanmean(lt_base))
        print('  S vs %-7s  mean_S=%6.1f  mean_base=%6.1f  '
              'stat=%s  p=%s'
              % (name, sm, bm,
                 'NaN' if np.isnan(stat) else '%.2f' % stat,
                 'NaN' if np.isnan(p) else '%.3g' % p))

    print('\nElapsed: %.1f s' % (time.perf_counter() - t0))


if __name__ == '__main__':
    main()
