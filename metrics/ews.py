"""Early-warning signal detectors for proposal #2.

Four detectors operate on a univariate time series ``x(t)`` sampled at
fixed ``dt_ms``:

- ``rolling_variance``: classical critical-slowing-down detector
  (Scheffer et al. 2009 *Nature*).
- ``rolling_ac1``: lag-1 autocorrelation, the other canonical EWS.
- ``rolling_spectral_entropy``: Welch PSD entropy in fixed window.
- ``S_from_dt``: the candidate detector ``log(1/dt(t))``, low-pass
  filtered and z-scored. Söderlind/Jay/Calvo (2015), Scheffel (2024) —
  see RESEARCH_DIRECTIONS.md Proposal #2.

The same ``rolling_*`` framework is reusable across all three baseline
detectors. ``population_rate`` extracts the binned firing-rate signal
that the detectors actually operate on in the pilot.
"""

import numpy as np
from scipy import signal


def population_rate(V_history, dt, V_reset, bin_ms=1.0):
    """Population firing rate, binned to ``bin_ms`` resolution.

    Parameters
    ----------
    V_history : ndarray, shape (n_steps, N)
        Per-step per-neuron voltage trace from ``state.history['V']``.
    dt : float
        Fixed integration timestep in seconds. (For adaptive-dt sims,
        pass a representative ``np.mean(state.dt_list)``; this function
        assumes uniform sampling.)
    V_reset : float
        Spike-reset voltage. A neuron is considered to have fired in
        step t when ``V[t-1] > V_reset`` and ``V[t] <= V_reset + 1e-9``.
    bin_ms : float
        Output bin width in milliseconds.

    Returns
    -------
    rate : ndarray
        Population rate (Hz, averaged across all neurons), shape
        (n_bins,).
    """
    V = np.asarray(V_history)
    above = V[:-1] > V_reset + 1e-9
    reset = V[1:] <= V_reset + 1e-9
    spike_step = above & reset  # shape (n_steps-1, N) bool
    bin_steps = max(int(round((bin_ms * 1e-3) / dt)), 1)
    n_bins = spike_step.shape[0] // bin_steps
    truncated = spike_step[:n_bins * bin_steps]
    counts = truncated.reshape(n_bins, bin_steps, -1).sum(axis=(1, 2))
    bin_dt = bin_steps * dt
    return counts / (V.shape[1] * bin_dt)


def resample_uniform(V_history, dt_list, dt_target_ms=1.0):
    """Resample a non-uniformly-timed per-step trace onto a uniform grid.

    Under adaptive Euler each row of ``V_history`` corresponds to a
    different ``dt``; the cumulative sum of ``dt_list`` recovers the
    absolute time of each row.

    Parameters
    ----------
    V_history : ndarray, shape (n_steps, N)
        Per-step per-neuron trace.
    dt_list : sequence of float
        Per-step dt; length ``n_steps - 1`` (the first row is t=0 init).
    dt_target_ms : float
        Output sample spacing in milliseconds.

    Returns
    -------
    t : ndarray, shape (n_out,)
    V_out : ndarray, shape (n_out, N)
    """
    V = np.asarray(V_history, dtype=np.float64)
    dts = np.asarray(dt_list, dtype=np.float64)
    n_steps, N = V.shape
    if dts.size == n_steps:
        t = np.concatenate(([0.0], np.cumsum(dts)))[:n_steps]
    elif dts.size == n_steps - 1:
        t = np.concatenate(([0.0], np.cumsum(dts)))
    else:
        raise ValueError('dt_list length %d incompatible with V_history '
                         '%d rows' % (dts.size, n_steps))
    t_target = np.arange(t[0], t[-1], dt_target_ms * 1e-3)
    if t_target.size < 2:
        return t_target, np.empty((0, N))
    V_out = np.empty((t_target.size, N), dtype=np.float64)
    for j in range(N):
        V_out[:, j] = np.interp(t_target, t, V[:, j])
    return t_target, V_out


def _rolling_apply(x, window_steps, step_steps, fn):
    n = x.shape[0]
    if n < window_steps:
        return np.empty(0)
    starts = np.arange(0, n - window_steps + 1, step_steps)
    return np.fromiter(
        (fn(x[s:s + window_steps]) for s in starts),
        dtype=np.float64,
        count=starts.shape[0],
    )


def rolling_variance(x, dt_ms, window_ms=200.0, step_ms=10.0):
    window_steps = max(int(round(window_ms / dt_ms)), 2)
    step_steps = max(int(round(step_ms / dt_ms)), 1)
    return _rolling_apply(np.asarray(x), window_steps, step_steps,
                          lambda w: float(np.var(w)))


def rolling_ac1(x, dt_ms, window_ms=200.0, step_ms=10.0):
    """Lag-1 autocorrelation in rolling windows."""
    def ac1(w):
        w = w - w.mean()
        denom = np.dot(w, w)
        if denom <= 0:
            return 0.0
        return float(np.dot(w[:-1], w[1:]) / denom)
    window_steps = max(int(round(window_ms / dt_ms)), 2)
    step_steps = max(int(round(step_ms / dt_ms)), 1)
    return _rolling_apply(np.asarray(x), window_steps, step_steps, ac1)


def rolling_spectral_entropy(x, dt_ms, window_ms=200.0, step_ms=10.0,
                              n_psd=256):
    """Shannon entropy of the Welch PSD in rolling windows.

    Higher entropy = whiter spectrum; lower entropy = peaked spectrum.
    """
    fs = 1000.0 / dt_ms
    def H(w):
        if w.std() < 1e-12:
            return 0.0
        nperseg = min(n_psd, len(w))
        _, P = signal.welch(w, fs=fs, nperseg=nperseg)
        P = P[P > 0]
        if P.size == 0:
            return 0.0
        p = P / P.sum()
        return float(-np.sum(p * np.log(p)))
    window_steps = max(int(round(window_ms / dt_ms)), 2)
    step_steps = max(int(round(step_ms / dt_ms)), 1)
    return _rolling_apply(np.asarray(x), window_steps, step_steps, H)


def S_from_dt(dt_list, dt_target_ms=1.0, lowpass_hz=100.0,
              zscore_window_ms=1000.0):
    """Candidate detector S(t) = log(1/dt(t)), resampled, low-passed,
    z-scored on a rolling window.

    Parameters
    ----------
    dt_list : sequence of float
        Per-step dt as written by the adaptive Euler stepper.
    dt_target_ms : float
        Output sample period in milliseconds. The dt stream is
        cumulatively integrated to recover simulated time and then
        linearly resampled onto a uniform grid.
    lowpass_hz : float
        Butterworth low-pass cutoff. Set to 0 to skip filtering.
    zscore_window_ms : float
        Rolling-window z-score length (1 s default per RESEARCH_DIRECTIONS).
    """
    dts = np.asarray(dt_list, dtype=np.float64)
    if dts.size == 0:
        return np.empty(0), np.empty(0)
    t = np.concatenate(([0.0], np.cumsum(dts)))[:-1]
    log_invdt = np.log(np.clip(1.0 / dts, 1e-30, None))

    t_target = np.arange(t[0], t[-1], dt_target_ms * 1e-3)
    if t_target.size < 2:
        return t_target, np.empty(t_target.shape)
    S = np.interp(t_target, t, log_invdt)

    fs = 1.0 / (dt_target_ms * 1e-3)
    if lowpass_hz > 0 and lowpass_hz < fs / 2:
        b, a = signal.butter(N=4, Wn=lowpass_hz / (fs / 2), btype='low')
        S = signal.filtfilt(b, a, S)

    window_steps = max(int(round(zscore_window_ms / dt_target_ms)), 2)
    if S.size > window_steps:
        S = _rolling_z(S, window_steps)
    else:
        S = (S - S.mean()) / max(S.std(), 1e-12)
    return t_target, S


def _rolling_z(x, w):
    """Per-sample z-score using a centered rolling mean/std of width w."""
    pad = w // 2
    xp = np.pad(x, pad, mode='reflect')
    out = np.empty_like(x)
    for i in range(x.size):
        seg = xp[i:i + w]
        m = seg.mean()
        s = seg.std()
        out[i] = (x[i] - m) / max(s, 1e-12)
    return out
