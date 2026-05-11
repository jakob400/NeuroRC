# Where this project stands and what to do next — 2026-05-11

A handoff synthesis. Read `DIAGNOSTICS.md` for the underlying data,
`PLAN.md` for the granular phase-by-phase status, and
`RESEARCH_DIRECTIONS.md` for the three publishable proposals.

## TL;DR (updated post fix-A + fix-B, 2026-05-11)

The simulation core is correct, fast, and well-tested (56 tests passing
in ~6 s under `uv run pytest`). Phases 0–2, Phase 3 shared minimum,
**Fix A** (V_thresh recalibration), and **Fix B** (slow K g_KIR + OU
cortical drive replacing Poisson) are all landed on `master`.

**Diagnostics now show:**

| Constraint | Pre-fix | Post-fix-B |
|---|---|---|
| D1: V_thresh calibration | broken (18 Hz/neuron) | **resolved** (1.57 Hz across an 8 mV V_thresh band) |
| D2: α×β feasibility | 1-2 / 24 cells | **24 / 24 cells** physiological |
| D3: dt observable range | 1.52 log units (4.6×) | 0.55 log units — worsened. **P2 abandon.** |
| D4: V_thresh knife-edge | 2 mV window | **8 mV wide robust band** |

Proposal #1 (AHP reservoir) is now pilot-ready. Proposal #2 (dt-as-
observable) should be abandoned in its original framing; the dt-range
finding folds into the P0 methods paper as a clean before/after result.
Proposal #3 (connectome atlas) still needs Fix C (Snudda + GRAPH-8).

**What's left to do (deferred to a later session):**

- `PUBLICATIONS.md` writing checklist for P0 (the methods paper that
  emerged from the diagnostic work).
- `figures/p0/` paper-grade figures generated from
  `scripts/p0_make_figures.py`.
- `data/p0/` CSV dumps of every numerical claim. (Diagnostic text dumps
  already landed; conversion to CSV is mechanical.)
- Optional: Brian2/NEURON portability spike for the "does this
  generalize" reviewer defense.

## Completed: fix A + fix B

Commits 863faf8 (Phase A), 85a07e7 (Phase B1 slow K), cb413bd (Phase B2
OU drive) on `master`. See `DIAGNOSTICS.md` post-fix-B sections under
each of D1, D2, D3, D4 for the before/after numbers.

Phase A (~30 minutes):
- `const.V_thresh = -0.041` (was `-0.042`). Justified by
  `scripts/diag_recalibrate_directed.py` under directed adjacency.
- LIF baselines `tests/baselines/lif_n2_k1_t1000_seed0.npy` and
  `tests/baselines/lif_n10_k4_p02_t1000_seed0.npy` regenerated.

Phase B1 (~2 hours):
- Slow K inward rectifier `g_KIR` added to STR (Wilson-Kawaguchi 1996;
  Mahon 2006). New `const.conductance_KIR_max=15 nS`,
  `voltage_KIR_half=-60 mV`, `_k_KIR=200 V^-1`, `_a_KIR=5 s^-1`.
- Plumbing through state.py, update_functions.py, integrators.py,
  logging_hdf5.py, dynamic_voltage_plot.py.
- `tests/test_bistability.py` covers rectification, state-carry,
  history shape.

Phase B2 (~1 hour):
- OU process replaces Poisson on `g_E` under new default
  `drive_mode='ou'`. `ou_tau=50 ms`, `ou_mean=3 nS`, `ou_sigma=4 nS`.
- Exact-discretization OU step in both update_functions and integrators;
  `g_E >= 0` clamp.
- `tests/test_drive_modes.py` covers all three modes.
- `scripts/diag_alpha_beta_grid.py` and
  `scripts/diag_recalibrate_directed.py` tMax bumped from 4000 (0.1 s,
  transient only) to 40000 (1.0 s, steady state).

## Decision point: P0 vs fix C vs pilots

With fix A + B landed, three forward paths:

- **Write P0 (methods paper).** *Recommended path.* The methods paper
  was always the publication floor and now has a clean before/after
  experimental structure: D1/D2/D4 resolved cleanly, D3 worsened
  honestly. ~2-3 weeks to manuscript with the existing diagnostic
  outputs.
- **Pilot P1 (AHP reservoir).** With α×β grid 24/24 feasible, the
  proposal-#1 experimental design is now runnable. 4-6 months to
  manuscript. Needs LIF-het + LIF-ALIF + IPC reimplementation.
- **Fix C: Snudda extraction + GRAPH-8 matching protocols.** 2-3 weeks
  to unlock proposal #3. Six-month scoop clock from Kotaleski lab.

For the per-paper deliverable breakdown — title, claim, target venue,
falsification criterion, and which engineering fixes each one needs —
see `PUBLICATIONS.md`.

## Per-proposal pilot success odds

Original (pre-fix) estimates retained for comparison; *current* column
reflects the post-fix-B state of the repo.

| Proposal | Pre-fix | After fix A only | After fix A+B (current) | After fix C |
|---|---|---|---|---|
| #1 AHP reservoir → Neural Comp 40–50 % | < 30 % | < 30 % | **65–75 %** | 65–75 % |
| #2 dt-as-observable → Front Neuroinform ~50 % | < 20 % | < 20 % | **Abandon original framing.** Range narrowed under fix B; D3 is structural. Salvage as P0 component. | n/a |
| #3 connectome atlas → Network Neurosci ~50 % | 50 % | 50 % | 50 % (no Snudda yet) | **70–75 %** |

## The 4th paper that emerged from the diagnostic work

> **"Bifurcation-induced infeasibility regions in threshold-reset
> spiking-network parameter sweeps: a calibration protocol and a
> dt-as-stiffness folklore quantification."**

Components (all already in the repo):

- `scripts/diag_alpha_beta_grid.py` — the 1-of-24 α × β finding
- `scripts/diag_recalibrate_directed.py` — V_thresh single-mV-window
- `scripts/diag_soderlind_separation.py` — dt dynamic-range budget
- `DIAGNOSTICS.md` — synthesis, citations of Söderlind & Scheffel

Target venue: Frontiers in Computational Neuroscience or PLOS Comp
Bio (Methods). Acceptance 50–60 %. ~2 weeks to manuscript draft
because everything reportable is already committed.

This is the publication *floor*: it survives no matter which of the
three main pilots fails. Mention this paper opportunity to anyone
considering whether to invest more time in the project.

## Recommended sequencing (updated post fix-B)

1. ~~Apply fix A immediately~~ — done (commit 863faf8).
2. ~~Spike fix B~~ — done (commits 85a07e7, cb413bd). AHP τ median
   dropped from 86 ms to 31 ms (closer to literature ~50 ms); firing
   became bursty (up-state clusters) at 0.67-1.6 Hz/neuron; α×β grid
   24/24 feasible.
3. **Write the P0 methods paper.** All four diagnostic findings (D1
   resolved, D2 resolved, D3 worsened-and-publishable, D4 resolved)
   now read as a clean experimental story with pre/post-fix-B tables
   already populated in `DIAGNOSTICS.md`. Manuscript drafting is
   off-repo; the repo-side support work is the P0-S phase of
   `/Users/jakob/.claude/plans/declarative-giggling-bentley.md`
   (figures, CSV dumps, optional Brian2 portability spike).
4. **Decide P1 vs P3 for the main paper.** P1 (AHP reservoir) is now
   pilot-ready and has a shorter path (4-6 months); P3 (connectome)
   has higher prestige but needs fix C first.
5. **P2 abandon.** D3 confirmed structurally; fold the dt-range
   measurement into P0 rather than pursuing the original Chaos /
   Front Neuroinform pitch.

## Things that are *not* serious threats (clarification)

These looked scary at various points but turn out to be fine:

- N=2 regression baseline has 0 edges — N=10 baseline (F3) covers
  the recurrent path.
- HDF5 storage scaling — only a problem at full proposal-#1 sweep
  scale; chunked logger is Phase 4 work.
- pytest under uv vs venv — confirmed identical results.
- Mean-degree formula for NWS — the doc's `k + 2p(N-k-1)` is wrong;
  NetworkX implements `k * (1 + p)`. Test in
  `tests/test_graph_build.py` uses the correct formula.

## File map for a picker-upper

| File | What it tells you |
|---|---|
| `README.md` | Quick start, doc map. |
| `CLAUDE.md` | Project overview and architecture. |
| `RESEARCH_DIRECTIONS.md` | The three publishable proposals + citations. |
| `IMPLEMENTATION.md` | The audit that motivated PLAN.md. |
| `PLAN.md` | 5-phase operational plan with per-item status. |
| `DIAGNOSTICS.md` | The four diagnostic runs from 2026-05-11 and what they imply. |
| `PUBLICATIONS.md` | Per-paper deliverable breakdown (P0–P3): claim, venue, falsification, time to manuscript, fixes needed. |
| `NEXT_STEPS.md` | *(this file)* The synthesis of where we are and what to do. |

Companion executables:
- `uv run pytest` — 49 tests, ~1.7 s
- `uv run python run.py` — interactive CLI (LIF/STR prompt)
- `uv run python -m scripts.phase1_biophysics_report` — biophysics
  sanity (BIO-1/2/3 targets)
- `uv run python -m scripts.diag_*` — the four diagnostics
- `uv run python -m scripts.proposal2_pilot_smoke` — EWS pipeline
  smoke test
- `uv run python -m scripts.proposal2_pilot` — reduced K-sweep pilot
