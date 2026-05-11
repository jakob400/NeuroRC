"""Tests for the metrics/ package."""

import numpy as np

from metrics import ews, oracles, stats


# ----- EWS detectors --------------------------------------------------

def test_rolling_variance_on_white_noise():
    """White noise should give roughly constant rolling variance."""
    rng = np.random.default_rng(0)
    x = rng.standard_normal(10000)
    v = ews.rolling_variance(x, dt_ms=1.0, window_ms=500.0, step_ms=50.0)
    assert v.size > 0
    assert v.min() > 0
    # Variance bounded near 1.0 +- 0.3 across windows
    assert abs(v.mean() - 1.0) < 0.3, v.mean()


def test_rolling_ac1_on_ar1():
    """AR(1) process with phi = 0.7 should give AC1 ~ 0.7."""
    rng = np.random.default_rng(0)
    n = 8000
    phi = 0.7
    x = np.zeros(n)
    eps = rng.standard_normal(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + eps[i]
    ac1 = ews.rolling_ac1(x, dt_ms=1.0, window_ms=500.0, step_ms=50.0)
    assert abs(ac1.mean() - phi) < 0.1, ac1.mean()


def test_rolling_spectral_entropy_peaked_vs_white():
    """A pure sine has lower spectral entropy than white noise."""
    rng = np.random.default_rng(0)
    t = np.arange(0, 8.0, 1e-3)
    sine = np.sin(2 * np.pi * 10 * t)
    white = rng.standard_normal(t.size)
    H_sine = ews.rolling_spectral_entropy(sine, dt_ms=1.0,
                                          window_ms=500.0, step_ms=50.0)
    H_white = ews.rolling_spectral_entropy(white, dt_ms=1.0,
                                           window_ms=500.0, step_ms=50.0)
    assert H_sine.mean() < H_white.mean(), (H_sine.mean(), H_white.mean())


def test_S_from_dt_basic():
    """Resampling and z-scoring leaves a roughly zero-mean signal."""
    rng = np.random.default_rng(0)
    # Many small dts plus a few spikes of small dt mimicking adaptive Euler
    dts = rng.uniform(2e-5, 3e-5, size=2000)
    # inject 'fast-dynamics bursts' (small dt -> large S)
    dts[800:820] = 5e-7
    t, S = ews.S_from_dt(dts, dt_target_ms=0.5, lowpass_hz=200.0,
                         zscore_window_ms=20.0)
    assert t.size > 0
    assert S.size == t.size
    assert abs(S.mean()) < 1.0
    # The injected burst should produce a positive excursion in S.
    assert S.max() > 1.5, S.max()


def test_population_rate_matches_construction():
    """Synthesize a V trace with known number of spikes and check rate."""
    n_steps, N = 5000, 100
    V = np.full((n_steps, N), -0.06, dtype=np.float64)
    # Force one spike per neuron at step 2500: V > V_reset then == V_reset
    V[2499, :] = -0.04
    V[2500, :] = -0.07  # V_reset
    dt = 25e-6
    rate = ews.population_rate(V, dt=dt, V_reset=-0.07, bin_ms=1.0)
    assert rate.shape[0] > 0
    assert rate.sum() > 0
    # Total spikes = N counts at step 2500 -> 100 in one 1 ms bin
    # Population rate (Hz) = 100 / (100 * 1e-3) = 1000 Hz peak
    assert rate.max() > 800, rate.max()


# ----- Kuramoto oracle ------------------------------------------------

def test_kuramoto_phase_locked_unity():
    """N identical sinusoids -> R = 1."""
    t = np.arange(0, 1.0, 1e-3)
    V = np.tile(np.sin(2 * np.pi * 5 * t)[:, None], (1, 10))
    R = oracles.kuramoto_order(V, dt=1e-3)
    # Skip Hilbert edge effects.
    assert R[100:-100].min() > 0.99


def test_kuramoto_random_phases_low():
    """Independent sinusoids with scrambled phases -> R << 1."""
    rng = np.random.default_rng(0)
    t = np.arange(0, 1.0, 1e-3)
    N = 50
    phases = rng.uniform(0, 2 * np.pi, size=N)
    V = np.stack([np.sin(2 * np.pi * 5 * t + p) for p in phases], axis=1)
    R = oracles.kuramoto_order(V, dt=1e-3)
    # Expected ~ 1/sqrt(N) for independent phases.
    assert R[100:-100].mean() < 0.3, R[100:-100].mean()


def test_first_crossing_with_dwell():
    x = np.array([0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1])
    # First sustained run of length 4 starts at index 4
    assert oracles.first_crossing(x, threshold=0.5, min_dwell_steps=4) == 4
    # No sustained run of length 5
    assert oracles.first_crossing(x, threshold=0.5, min_dwell_steps=5) == -1


# ----- Stats ----------------------------------------------------------

def test_lead_time_basic():
    """Detector crosses threshold 50 samples before transition."""
    n = 1000
    transition = 500
    d = np.zeros(n)
    d[450:] = 5.0  # crosses at sample 450, 50 before transition
    lt = stats.lead_time_at_fpr(d, transition, fpr_threshold=0.05)
    assert lt == 50


def test_lead_time_no_transition_returns_nan():
    d = np.zeros(1000)
    lt = stats.lead_time_at_fpr(d, -1)
    assert np.isnan(lt)


def test_wilcoxon_drops_nan_pairs():
    a = [10.0, 20.0, 30.0, float('nan'), 50.0, 60.0, 70.0]
    b = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0]
    stat, p = stats.wilcoxon_compare(a, b)
    assert np.isfinite(stat)
    assert np.isfinite(p)
    assert p < 0.5


def test_roc_auc_perfect_detector():
    """Detector that ramps up exactly before the transition has AUC=1."""
    n = 1000
    transition = 500
    d = np.zeros(n)
    d[:transition] = np.linspace(0, 1, transition)
    auc = stats.roc_auc_sliding(d, transition, label_horizon_steps=100)
    assert auc > 0.99
