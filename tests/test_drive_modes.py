"""B2: Drive-mode plumbing tests.

Three drive modes coexist in const.drive_mode: 'constant', 'poisson', 'ou'.
The simulator must dispatch each correctly:

  - constant: legacy +I term in func_E; g_E relaxes toward I/_a_E.
  - poisson: shot-noise kicks; long-run mean approaches
    poisson_rate * poisson_delta_g_E / _a_E.
  - ou: g_E follows an OU process; stationary mean and std match
    ou_mean and ou_sigma to within MC tolerance.
"""

import numpy as np
import pytest

import const
from simulate import simulate


def _override(**kwargs):
    saved = {k: getattr(const, k) for k in kwargs}
    for k, v in kwargs.items():
        setattr(const, k, v)
    return saved


def _restore(saved):
    for k, v in saved.items():
        setattr(const, k, v)


def test_constant_drive_mode_relaxes_g_E_to_steady_state():
    """g_E -> I/_a_E under constant drive. Approximation due to recurrent
    inhibition coupling; check order of magnitude."""
    saved = _override(drive_mode='constant')
    try:
        G, s = simulate('STR', N=10, K=2, P=0.1, tMax=2000, seed=0,
                        fixed_dt_mode=True)
    finally:
        _restore(saved)
    g_E = np.asarray(s.history['g_E'])
    expected_ss = const.I / const._a_E   # = 1e-3 / 1e3 = 1e-6 S
    final = g_E[-200:].mean()
    assert 0.5 * expected_ss < final < 2.0 * expected_ss, (final, expected_ss)


def test_poisson_drive_mode_mean_matches_lambda_over_a():
    """Long-run mean g_E under Poisson kicks approaches
    rate * delta / _a_E to within MC tolerance."""
    saved = _override(drive_mode='poisson')
    try:
        G, s = simulate('STR', N=100, K=10, P=0.1, tMax=20000, seed=0,
                        fixed_dt_mode=True)
    finally:
        _restore(saved)
    g_E = np.asarray(s.history['g_E'])
    expected_mean = const.poisson_rate * const.poisson_delta_g_E / const._a_E
    final_mean = g_E[-5000:].mean()
    assert 0.5 * expected_mean < final_mean < 1.5 * expected_mean, \
        (final_mean, expected_mean)


def test_ou_drive_mode_stationary_distribution():
    """Long-run g_E under OU drive has mean ~ ou_mean and std ~ ou_sigma.
    The >= 0 clamp causes slight upward bias on the mean and slight std
    deflation when ou_mean is within a few sigma of zero; allow a 50%
    tolerance band on both."""
    saved = _override(drive_mode='ou')
    try:
        G, s = simulate('STR', N=200, K=20, P=0.1, tMax=40000, seed=0,
                        fixed_dt_mode=True)
    finally:
        _restore(saved)
    g_E = np.asarray(s.history['g_E'])
    # Drop initial 200 ms (8000 steps at 25us) for OU relaxation.
    g_E_ss = g_E[8000:]
    mean = g_E_ss.mean()
    std = g_E_ss.std()
    # Stationary mean comes out higher than ou_mean because of >=0 clamp
    # when ou_mean is close to zero relative to ou_sigma. Verify it's in
    # the right neighborhood and the std reflects the OU's variance.
    assert const.ou_mean < mean < 2.0 * const.ou_mean, \
        (mean, const.ou_mean)
    assert 0.5 * const.ou_sigma < std < 1.5 * const.ou_sigma, \
        (std, const.ou_sigma)
    assert g_E_ss.min() >= 0.0, g_E_ss.min()


def test_ou_drive_reproducible_across_runs():
    """Same seed -> identical g_E trajectories under OU drive."""
    saved = _override(drive_mode='ou')
    try:
        G1, s1 = simulate('STR', N=10, K=2, P=0.1, tMax=500, seed=42,
                          fixed_dt_mode=True)
        G2, s2 = simulate('STR', N=10, K=2, P=0.1, tMax=500, seed=42,
                          fixed_dt_mode=True)
    finally:
        _restore(saved)
    g_E1 = np.asarray(s1.history['g_E'])
    g_E2 = np.asarray(s2.history['g_E'])
    np.testing.assert_allclose(g_E1, g_E2, atol=0, rtol=0)
