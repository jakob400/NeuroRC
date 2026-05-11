"""Diagnostic: sweep V_thresh under post-GRAPH-3 directed adjacency
to find a 1 Hz/neuron operating point.

The F1 calibration (V_thresh = -42 mV) was tuned under undirected NWS
where each edge contributed to A in both directions. The GRAPH-3
correction (A[postsyn, presyn] = w with one direction per edge in a
DiGraph) halves the recurrent inhibition density. F7 just measured
18 Hz/neuron at default V_thresh -- the calibration is broken.

This sweep finds the new V_thresh that lands the directed network at
0.5-2 Hz/neuron, if any.
"""

import numpy as np

import const
from simulate import simulate


def measure(V_th, N=200, K=20, P=0.1, tMax=4000, seed=0):
    saved = const.V_thresh
    const.V_thresh = V_th
    try:
        G, s = simulate('STR', N=N, K=K, P=P, tMax=tMax, seed=seed,
                        fixed_dt_mode=True)
    finally:
        const.V_thresh = saved
    V = np.asarray(s.history['V'])
    spikes = ((V[:-1] > const.V_reset + 1e-9)
              & (V[1:] <= const.V_reset + 1e-9)).sum()
    sim_s = V.shape[0] * const.dt_fixed
    return spikes / N / sim_s


def main():
    print('=== V_thresh re-calibration under directed adjacency ===')
    print('Default V_thresh in const.py: %.1f mV' % (const.V_thresh * 1000))
    print()
    print('%-9s %s' % ('V_thresh', 'rate (Hz/neuron)'))
    for V_th in (-0.038, -0.040, -0.041, -0.042, -0.043, -0.044,
                 -0.045, -0.046, -0.048, -0.050, -0.055):
        r = measure(V_th)
        tag = ' <-- physio' if 0.5 <= r <= 2.0 else ''
        print('%-9.1f %.3f%s' % (V_th * 1000, r, tag))


if __name__ == '__main__':
    main()
