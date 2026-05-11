"""Statistical comparison primitives for proposal #2 lead-time analysis.

Wilcoxon signed-rank (paired across seeds), ROC AUC for the
"transition within next 100 ms" sliding-label task, and lead-time at
fixed false-positive rate.
"""

import numpy as np
from scipy import stats as sp_stats


def lead_time_at_fpr(detector, transition_step, fpr_threshold=0.05,
                     pre_transition_only=True):
    """Return ``transition_step - first_crossing`` of the
    detector threshold calibrated to deliver false-positive rate
    ``fpr_threshold`` on the pre-transition baseline.

    Parameters
    ----------
    detector : ndarray, shape (n_steps,)
        Time-aligned detector output (e.g., S(t) z-scored).
    transition_step : int
        Index of the ground-truth oracle crossing. -1 means no
        transition observed within the window (returns NaN).
    fpr_threshold : float
        Target false-positive rate on the pre-transition baseline.
    pre_transition_only : bool
        If True, compute the threshold using only samples before
        ``transition_step`` (this is the only honest way).

    Returns
    -------
    float
        Lead time in samples. NaN if no transition.
    """
    if transition_step < 0:
        return float('nan')
    d = np.asarray(detector)
    baseline = d[:transition_step] if pre_transition_only else d
    if baseline.size == 0:
        return float('nan')
    threshold = np.quantile(baseline, 1 - fpr_threshold)
    above = d >= threshold
    crossings = np.flatnonzero(above)
    if crossings.size == 0:
        return float('nan')
    first = int(crossings[0])
    return float(transition_step - first)


def wilcoxon_compare(lead_times_a, lead_times_b):
    """Two-sided Wilcoxon signed-rank on paired lead times.

    Drops pairs containing NaN. Returns (statistic, p_value).
    """
    a = np.asarray(lead_times_a, dtype=np.float64)
    b = np.asarray(lead_times_b, dtype=np.float64)
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 6:
        return float('nan'), float('nan')
    res = sp_stats.wilcoxon(a[mask], b[mask], alternative='two-sided')
    return float(res.statistic), float(res.pvalue)


def roc_auc_sliding(detector, transition_step, label_horizon_steps):
    """ROC AUC for the binary task: 'is a transition within the next
    ``label_horizon_steps`` samples?'

    Returns NaN if either class is empty (e.g., no transition).
    """
    d = np.asarray(detector)
    n = d.shape[0]
    if transition_step < 0:
        return float('nan')
    labels = np.zeros(n, dtype=np.int8)
    start = max(transition_step - label_horizon_steps, 0)
    labels[start:transition_step] = 1
    pos = (labels == 1)
    neg = (labels == 0)
    if not pos.any() or not neg.any():
        return float('nan')
    # Mann-Whitney U / (n_pos * n_neg) is identical to ROC AUC.
    u, _ = sp_stats.mannwhitneyu(d[pos], d[neg], alternative='greater')
    return float(u / (pos.sum() * neg.sum()))
