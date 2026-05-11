"""Analysis metrics package.

Houses the per-proposal analysis pipelines:

- ``ews``: Pipeline B (proposal #2) early-warning signal detectors and the
  dt-based candidate detector ``S(t) = log(1/dt(t))``.
- ``oracles``: ground-truth oracles for the proposal #2 pilot — Kuramoto
  order parameter from Hilbert-transformed Vm, etc.
- ``stats``: Wilcoxon signed-rank, ROC AUC, lead-time at fixed FPR.

The reservoir pipeline (proposal #1, ``ANA-5``) and spike-train pipeline
(proposal #3, ``ANA-8``) will land separately when those pilots run.
"""
