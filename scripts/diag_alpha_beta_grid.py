"""Diagnostic: STR firing rate over the proposal #1 alpha x beta grid.

RESEARCH_DIRECTIONS.md proposal #1 plans:
  alpha in {0, 0.25, 0.5, 1, 2, 4} x conductance_A_max
  beta  in {0, 0.5, 1, 2}          x conductance_K_max
  (6 x 4 = 24 cells)

For the comparison to be meaningful every cell must fire at a
physiological 0.5-2 Hz/neuron under rate matching. This script
checks how many cells already lie in that window at default Poisson
drive (no rate matching) -- i.e. the feasible region for the sweep.

A cell is:
  - silent if rate <= 0.1 Hz/neuron
  - physiological if 0.5 <= rate <= 5 Hz/neuron
  - hyper if rate > 20 Hz/neuron (refractory-limited)
"""

import time

import numpy as np

import const
from simulate import simulate


ALPHAS = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
BETAS = [0.0, 0.5, 1.0, 2.0]
N_NODES = 100
# 40000 * 25 us = 1.0 s. The OU drive's 50 ms autocorrelation and the
# slow-K (KIR) 200 ms time constant both need many tau to reach steady
# state; the prior 0.1 s window caught only the initial transient.
TMAX = 40000
SEED = 0
V_THRESH_OVERRIDE = -0.041  # post-GRAPH-3 calibration; override at runtime


def measure_rate(alpha, beta):
    saved_A = const.conductance_A_max
    saved_K = const.conductance_K_max
    saved_Vt = const.V_thresh
    const.conductance_A_max = alpha * saved_A
    const.conductance_K_max = beta * saved_K
    const.V_thresh = V_THRESH_OVERRIDE
    try:
        G, s = simulate('STR', N=N_NODES, K=20, P=0.1, tMax=TMAX,
                        seed=SEED, fixed_dt_mode=True)
    finally:
        const.conductance_A_max = saved_A
        const.conductance_K_max = saved_K
        const.V_thresh = saved_Vt
    V = np.asarray(s.history['V'])
    spikes = ((V[:-1] > const.V_reset + 1e-9)
              & (V[1:] <= const.V_reset + 1e-9)).sum()
    sim_s = V.shape[0] * const.dt_fixed
    return spikes / N_NODES / sim_s


def classify(rate):
    if rate <= 0.1:
        return 'silent'
    if 0.5 <= rate <= 5.0:
        return 'physio'
    if rate > 20.0:
        return 'hyper'
    return 'between'


def main():
    print('=== Proposal #1 alpha x beta feasibility ===')
    print('Default conductance_A_max=%.2g, conductance_K_max=%.2g'
          % (const.conductance_A_max, const.conductance_K_max))
    print('N=%d, K=20, P=0.1, tMax=%d steps' % (N_NODES, TMAX))
    print()
    print('%6s' % 'alpha\\beta', end='')
    for b in BETAS:
        print(' %10s' % ('beta=%.2g' % b), end='')
    print()

    counts = {'silent': 0, 'physio': 0, 'hyper': 0, 'between': 0}
    t0 = time.perf_counter()
    for a in ALPHAS:
        print('%-6.2g' % a, end='')
        for b in BETAS:
            r = measure_rate(a, b)
            cat = classify(r)
            counts[cat] += 1
            tag = {'silent': 'S', 'physio': 'P', 'hyper': 'H',
                   'between': '.'}[cat]
            print(' %8.2f [%s]' % (r, tag), end='')
        print()

    print('\nLegend: S=silent (<=0.1 Hz), P=physio (0.5-5 Hz), '
          'H=hyper (>20 Hz)')
    total = sum(counts.values())
    print('Feasibility: %d/%d cells physiological '
          '(silent=%d, hyper=%d, between=%d).' %
          (counts['physio'], total, counts['silent'],
           counts['hyper'], counts['between']))
    print('Elapsed: %.1f s' % (time.perf_counter() - t0))


if __name__ == '__main__':
    main()
