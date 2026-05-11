"""P0 methods-paper figure generator.

Regenerates every figure in publications/p0_methods/figures/ and every
CSV in publications/p0_methods/data/ from a clean checkout. Seed-pinned
for reproducibility. Wall clock ~3-4 min on the dev laptop.

Figures (saved as both 300 dpi PNG and vector SVG):
  - alpha_beta_heatmap.{png,svg}: 6x4 grid feasibility, pre vs post fix-B.
  - v_thresh_sensitivity.{png,svg}: rate vs V_thresh, pre vs post fix-B.
  - v_histogram.{png,svg}: bimodal up/down state V distribution post-fix-B.
  - dt_kde.{png,svg}: log(1/dt) kernel density across regimes.

CSVs (one per numerical claim used in the manuscript):
  - alpha_beta_grid_pre.csv  / alpha_beta_grid_post.csv
  - v_thresh_sweep_pre.csv   / v_thresh_sweep_post.csv
  - v_histogram_post.csv
  - dt_ranges.csv

Pre-fix-B condition: conductance_KIR_max=0 (slow K disabled) and
drive_mode='poisson'. This isolates the fix-B contribution.

Usage:
    uv run python publications/p0_methods/scripts/make_figures.py
"""

import csv
import os
import sys
import time
from pathlib import Path

# Add src/ to sys.path so this script can `import const`, `from simulate ...`.
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np

import const
from simulate import simulate


# Output paths are anchored to the paper directory, not cwd, so the script
# works regardless of where it's invoked from.
_PAPER_DIR = Path(__file__).resolve().parents[1]
FIG_DIR = str(_PAPER_DIR / 'figures')
DATA_DIR = str(_PAPER_DIR / 'data')

PRE_FIX_B = dict(
    drive_mode='poisson',
    conductance_KIR_max=0.0,  # disables slow K
    V_thresh=-0.042,           # pre-fix-A calibration (post-GRAPH-3)
)
POST_FIX_B = dict(
    drive_mode='ou',
    conductance_KIR_max=15e-9,
    V_thresh=-0.041,
)


def _override(overrides):
    saved = {k: getattr(const, k) for k in overrides}
    for k, v in overrides.items():
        setattr(const, k, v)
    return saved


def _restore(saved):
    for k, v in saved.items():
        setattr(const, k, v)


def _save(fig, name):
    fig.savefig(os.path.join(FIG_DIR, name + '.png'), dpi=300,
                bbox_inches='tight')
    fig.savefig(os.path.join(FIG_DIR, name + '.svg'),
                bbox_inches='tight')
    plt.close(fig)


def _write_csv(path, header, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def measure_rate(N=100, tMax=40000, seed=0):
    G, s = simulate('STR', N=N, K=20, P=0.1, tMax=tMax, seed=seed,
                    fixed_dt_mode=True)
    V = np.asarray(s.history['V'])
    spikes = ((V[:-1] > const.V_reset + 1e-9)
              & (V[1:] <= const.V_reset + 1e-9)).sum()
    sim_s = V.shape[0] * const.dt_fixed
    return spikes / N / sim_s, V


def alpha_beta_grid(overrides):
    saved = _override(overrides)
    alphas = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
    betas = [0.0, 0.5, 1.0, 2.0]
    rates = np.zeros((len(alphas), len(betas)))
    A0 = saved['conductance_A_max'] if 'conductance_A_max' in saved else const.conductance_A_max
    K0 = saved['conductance_K_max'] if 'conductance_K_max' in saved else const.conductance_K_max
    saved_A = const.conductance_A_max
    saved_K = const.conductance_K_max
    try:
        for i, a in enumerate(alphas):
            for j, b in enumerate(betas):
                const.conductance_A_max = a * saved_A
                const.conductance_K_max = b * saved_K
                r, _ = measure_rate(N=100, tMax=40000)
                rates[i, j] = r
    finally:
        const.conductance_A_max = saved_A
        const.conductance_K_max = saved_K
        _restore(saved)
    return alphas, betas, rates


def fig_alpha_beta_heatmap():
    print('[1/4] alpha-beta heatmap (2x grid, 24 cells each) ...')
    t0 = time.perf_counter()
    a_pre, b_pre, rates_pre = alpha_beta_grid(PRE_FIX_B)
    a_post, b_post, rates_post = alpha_beta_grid(POST_FIX_B)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    vmin, vmax = 0.0, 30.0
    for ax, rates, title in [
        (axes[0], rates_pre, 'Pre fix-B (Poisson, no g_KIR)'),
        (axes[1], rates_post, 'Post fix-B (OU, g_KIR=15 nS)'),
    ]:
        im = ax.imshow(rates, aspect='auto', origin='lower',
                       cmap='viridis', vmin=vmin, vmax=vmax,
                       extent=[-0.5, len(b_post) - 0.5,
                               -0.5, len(a_post) - 0.5])
        ax.set_xticks(range(len(b_post)))
        ax.set_xticklabels([str(b) for b in b_post])
        ax.set_yticks(range(len(a_post)))
        ax.set_yticklabels([str(a) for a in a_post])
        ax.set_xlabel(r'$\beta$ (K-channel scale)')
        ax.set_title(title)
        # Annotate physio cells
        for i in range(len(a_post)):
            for j in range(len(b_post)):
                r = rates[i, j]
                tag = 'P' if 0.5 <= r <= 5.0 else ('H' if r > 20 else 'S')
                color = 'white' if r < 15 else 'black'
                ax.text(j, i, '%.1f' % r, ha='center', va='center',
                        fontsize=8, color=color)
    axes[0].set_ylabel(r'$\alpha$ (AHP scale)')
    fig.colorbar(im, ax=axes, label='Firing rate (Hz/neuron)', shrink=0.8)
    _save(fig, 'alpha_beta_heatmap')

    # CSVs
    _write_csv(os.path.join(DATA_DIR, 'alpha_beta_grid_pre.csv'),
               ['alpha', 'beta', 'rate_hz_per_neuron'],
               [(a, b, rates_pre[i, j])
                for i, a in enumerate(a_pre)
                for j, b in enumerate(b_pre)])
    _write_csv(os.path.join(DATA_DIR, 'alpha_beta_grid_post.csv'),
               ['alpha', 'beta', 'rate_hz_per_neuron'],
               [(a, b, rates_post[i, j])
                for i, a in enumerate(a_post)
                for j, b in enumerate(b_post)])
    print('    %.1f s' % (time.perf_counter() - t0))


def v_thresh_sweep(overrides, V_threshes):
    saved = _override(overrides)
    rates = []
    try:
        for V_th in V_threshes:
            const.V_thresh = V_th
            r, _ = measure_rate(N=200, tMax=40000)
            rates.append(r)
    finally:
        _restore(saved)
    return np.array(rates)


def fig_v_thresh_sensitivity():
    print('[2/4] V_thresh sensitivity sweep ...')
    t0 = time.perf_counter()
    V_threshes = np.array([-0.038, -0.040, -0.041, -0.042, -0.043, -0.044,
                           -0.045, -0.046, -0.048, -0.050])
    rates_pre = v_thresh_sweep(PRE_FIX_B, V_threshes)
    rates_post = v_thresh_sweep(POST_FIX_B, V_threshes)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(V_threshes * 1000, np.maximum(rates_pre, 1e-3),
                marker='o', label='Pre fix-B (Poisson, no g_KIR)',
                color='#d95f02')
    ax.semilogy(V_threshes * 1000, np.maximum(rates_post, 1e-3),
                marker='s', label='Post fix-B (OU, g_KIR)',
                color='#1b9e77')
    ax.axhspan(0.5, 5.0, color='gray', alpha=0.15,
               label='Physiological band')
    ax.set_xlabel(r'$V_{\mathrm{thresh}}$ (mV)')
    ax.set_ylabel('Firing rate (Hz/neuron, log scale)')
    ax.set_title('V_thresh sensitivity: knife-edge vs robust band')
    ax.legend(loc='lower right', fontsize=9)
    _save(fig, 'v_thresh_sensitivity')

    _write_csv(os.path.join(DATA_DIR, 'v_thresh_sweep_pre.csv'),
               ['V_thresh_mV', 'rate_hz_per_neuron'],
               list(zip((V_threshes * 1000).tolist(), rates_pre.tolist())))
    _write_csv(os.path.join(DATA_DIR, 'v_thresh_sweep_post.csv'),
               ['V_thresh_mV', 'rate_hz_per_neuron'],
               list(zip((V_threshes * 1000).tolist(), rates_post.tolist())))
    print('    %.1f s' % (time.perf_counter() - t0))


def fig_v_histogram():
    print('[3/4] V histogram (up/down state distribution) ...')
    t0 = time.perf_counter()
    # Pre fix-B: Poisson, no g_KIR. Run long enough to fill histogram.
    saved = _override(PRE_FIX_B)
    try:
        _, V_pre = measure_rate(N=200, tMax=40000)
    finally:
        _restore(saved)
    saved = _override(POST_FIX_B)
    try:
        _, V_post = measure_rate(N=200, tMax=40000)
    finally:
        _restore(saved)

    bins = np.linspace(-0.080, -0.040, 81)
    # Exclude refractory clamp at V_reset (-0.070): only count V > V_reset+0.5mV.
    pre_flat = V_pre.ravel()
    post_flat = V_post.ravel()
    pre_active = pre_flat[pre_flat > const.V_reset + 0.5e-3]
    post_active = post_flat[post_flat > const.V_reset + 0.5e-3]

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(pre_active * 1000, bins=bins * 1000, alpha=0.5, density=True,
            label='Pre fix-B (unimodal)', color='#d95f02')
    ax.hist(post_active * 1000, bins=bins * 1000, alpha=0.5, density=True,
            label='Post fix-B (bistable)', color='#1b9e77')
    ax.axvline(-60, color='gray', linestyle=':',
               label=r'$V_{\mathrm{KIR,half}}$')
    ax.set_xlabel('Membrane potential V (mV)')
    ax.set_ylabel('Density (excluding refractory clamp)')
    ax.set_title('Bimodality emerges with fix B')
    ax.legend(loc='upper left', fontsize=9)
    _save(fig, 'v_histogram')

    counts_pre, edges = np.histogram(pre_active, bins=bins, density=True)
    counts_post, _ = np.histogram(post_active, bins=bins, density=True)
    centers = 0.5 * (edges[:-1] + edges[1:])
    _write_csv(os.path.join(DATA_DIR, 'v_histogram_post.csv'),
               ['V_mV', 'density_pre', 'density_post'],
               list(zip((centers * 1000).tolist(),
                        counts_pre.tolist(),
                        counts_post.tolist())))
    print('    %.1f s' % (time.perf_counter() - t0))


def measure_dt_ranges(overrides, tMax=40000):
    saved = _override({**overrides, 'fixed_dt_mode': False})
    try:
        G, s = simulate('STR', N=100, K=20, P=0.1, tMax=tMax, seed=0)
        dts = np.asarray(s.dt_list)
    finally:
        _restore(saved)
    dts = dts[dts > 0]
    log_inv_dt = -np.log(dts)
    return log_inv_dt


def fig_dt_kde():
    print('[4/4] log(1/dt) KDE across regimes ...')
    t0 = time.perf_counter()
    pre = measure_dt_ranges(PRE_FIX_B, tMax=20000)
    post = measure_dt_ranges(POST_FIX_B, tMax=20000)
    pre_range = float(pre.max() - pre.min())
    post_range = float(post.max() - post.min())

    fig, ax = plt.subplots(figsize=(6.5, 4))
    bins = np.linspace(min(pre.min(), post.min()),
                       max(pre.max(), post.max()), 80)
    ax.hist(pre, bins=bins, alpha=0.5, density=True,
            label='Pre fix-B (Poisson, no g_KIR): range %.2f' % pre_range,
            color='#d95f02')
    ax.hist(post, bins=bins, alpha=0.5, density=True,
            label='Post fix-B (OU, g_KIR): range %.2f' % post_range,
            color='#1b9e77')
    ax.set_xlabel(r'$\log(1/dt)$ (log seconds$^{-1}$)')
    ax.set_ylabel('Density')
    ax.set_title('Adaptive dt observable: dynamic range narrows under fix B')
    ax.legend(loc='upper right', fontsize=9)
    _save(fig, 'dt_kde')

    _write_csv(os.path.join(DATA_DIR, 'dt_ranges.csv'),
               ['condition', 'log_inv_dt_min', 'log_inv_dt_max',
                'log_inv_dt_range', 'dt_ratio'],
               [
                ('pre_fix_b', float(pre.min()), float(pre.max()),
                 pre_range, float(np.exp(pre_range))),
                ('post_fix_b', float(post.min()), float(post.max()),
                 post_range, float(np.exp(post_range))),
               ])
    print('    %.1f s' % (time.perf_counter() - t0))


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    t0 = time.perf_counter()
    fig_alpha_beta_heatmap()
    fig_v_thresh_sensitivity()
    fig_v_histogram()
    fig_dt_kde()
    print('Total: %.1f s' % (time.perf_counter() - t0))
    print('Figures in %s/, CSVs in %s/' % (FIG_DIR, DATA_DIR))


if __name__ == '__main__':
    main()
