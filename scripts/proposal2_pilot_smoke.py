"""Smoke test for the Proposal #2 EWS pipeline.

End-to-end exercise of the metrics/ package against a real adaptive-dt
NWS simulation. NOT the actual pilot — just confirms the pipeline runs
and prints summary statistics. The actual pilot (synchronization-onset
K-sweep, 50 seeds x 30 K-values) plugs the same primitives into a sweep
harness.

Usage:
    uv run python -m scripts.proposal2_pilot_smoke
"""

import time

import numpy as np

import const
from simulate import simulate
from metrics import ews, oracles, stats


def run_one(N=200, K=8, P=0.05, tMax=100000, seed=0):
    """One adaptive-Euler LIF simulation, returns (state, dt_target_ms)."""
    t0 = time.perf_counter()
    G, state = simulate('LIF', N=N, K=K, P=P, tMax=tMax, seed=seed,
                        fixed_dt_mode=False)
    print('  sim: N=%d, K=%d, P=%g, tMax=%d, seed=%d  '
          'wall=%.2fs sim_s=%.4fs' % (
              N, K, P, tMax, seed,
              time.perf_counter() - t0, sum(state.dt_list)))
    return G, state


def main():
    print('=== Proposal #2 pipeline smoke test ===')
    print('V_thresh=%.1fmV, dt_floor=%.2g, dt_max=%.2g' %
          (const.V_thresh * 1000, const.dt_floor, const.dt_max))

    G, state = run_one()
    dt_target_ms = 0.5
    dts = np.asarray(state.dt_list)
    V_hist = np.asarray(state.history['V'])

    # Resample to uniform grid for baseline detectors.
    t_uniform, V_uniform = ews.resample_uniform(V_hist, dts,
                                                dt_target_ms=dt_target_ms)
    print('  resampled grid: %d points at %.2f ms (%.3f s total)'
          % (t_uniform.size, dt_target_ms, t_uniform[-1]))

    # Detector pipeline.
    r = ews.population_rate(V_uniform, dt=dt_target_ms * 1e-3,
                            V_reset=const.V_reset, bin_ms=1.0)
    print('  population rate: mean=%.2f Hz, max=%.2f Hz, n_bins=%d'
          % (r.mean(), r.max(), r.size))

    sigma2 = ews.rolling_variance(r, dt_ms=1.0, window_ms=200.0,
                                  step_ms=10.0)
    ac1 = ews.rolling_ac1(r, dt_ms=1.0, window_ms=200.0, step_ms=10.0)
    H = ews.rolling_spectral_entropy(r, dt_ms=1.0, window_ms=200.0,
                                     step_ms=10.0)
    t_S, S = ews.S_from_dt(dts, dt_target_ms=dt_target_ms,
                           lowpass_hz=100.0, zscore_window_ms=200.0)

    print('  baseline detectors:')
    print('    sigma^2: shape=%s, range=[%.3g, %.3g]'
          % (sigma2.shape, sigma2.min(), sigma2.max()))
    print('    AC(1):   shape=%s, range=[%.3f, %.3f]'
          % (ac1.shape, ac1.min(), ac1.max()))
    print('    H_spec:  shape=%s, range=[%.3f, %.3f]'
          % (H.shape, H.min(), H.max()))
    print('    S(t):    shape=%s, range=[%.3f, %.3f]'
          % (S.shape, S.min(), S.max()))

    # Kuramoto oracle on resampled Vm. With a stable quiescent network
    # we don't expect a real transition — this just exercises the path.
    R = oracles.kuramoto_order(V_uniform, dt=dt_target_ms * 1e-3)
    print('  Kuramoto order: mean=%.3f, max=%.3f' % (R.mean(), R.max()))
    transition = oracles.first_crossing(R, threshold=0.5,
                                        min_dwell_steps=int(50 / dt_target_ms))
    print('  first sustained R>=0.5 crossing: %s'
          % (transition if transition >= 0 else 'none observed'))

    if transition >= 0 and S.size > 0:
        # Align S(t) length to transition index space (different sampling
        # grids: r/sigma2/AC1/H are on r's 1 ms grid; S is on dt_target_ms grid).
        lt_S = stats.lead_time_at_fpr(S, min(transition, S.size - 1))
        print('  lead-time S(t) at 5%% FPR: %s'
              % ('%.1f samples' % lt_S if np.isfinite(lt_S) else 'NaN'))
    else:
        print('  no transition -> lead-time calc skipped (expected for '
              'a stable LIF network at default Poisson drive)')

    print('=== smoke test complete; pipeline integrates end-to-end ===')


if __name__ == '__main__':
    main()
