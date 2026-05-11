# Where this project stands and what to do next — 2026-05-11

A handoff synthesis. Read `DIAGNOSTICS.md` for the underlying data,
`PLAN.md` for the granular phase-by-phase status, and
`RESEARCH_DIRECTIONS.md` for the three publishable proposals.

## TL;DR

The simulation core is correct, fast, and well-tested (49 tests
passing in ~1.7 s under `uv run pytest`). Phases 0–2 of `PLAN.md` are
done, Phase 3 shared minimum (graph dispatch, lognormal weights,
NWS-as-DiGraph, modular SBM, MS-rewire) is done, the `metrics/`
package scaffolds proposal #2's EWS pipeline.

**But** four diagnostics (see `DIAGNOSTICS.md`) surfaced three real
constraints that change what is actually publishable:

1. **The V_thresh = -42 mV calibration is broken** after GRAPH-3's
   directed-adjacency fix. Network now fires at 18 Hz/neuron instead
   of 1 Hz. Mechanical to fix; ~2 hours of work.
2. **The proposal-#1 α × β grid has 1–2 of 24 cells in the
   physiological firing window.** The bifurcation in
   threshold-reset + Poisson drive is intrinsic; no V_thresh value
   tiles the grid smoothly. Structural, not mechanical.
3. **`S(t) = log(1/dt)` varies by ≤ 4.6×** across an entire run. The
   noise floor is ~10 % relative. Proposal #2's detector does not
   have the dynamic range to compete with the EWS baselines it is
   supposed to beat.

The biggest single risk-reducer for #2 and #3 simultaneously is
**adding up/down state dynamics to STR** (slow K conductance with
V-gated activation; ~30 LOC, 2–3 days; biology is from
Wilson & Kawaguchi 1996, Mahon 2006). That:

- Opens the α × β grid (knobs become smooth, not step functions)
- Gives the dt observable orders-of-magnitude dynamic range
  (down-state quiescence vs up-state bursts)
- Strengthens the biological framing for all three proposals

## Immediate next action (fix A, ~2 hours)

Re-apply the calibration that GRAPH-3 invalidated.

1. Set `const.V_thresh = -0.041` (was `-0.042`). Justified by
   `scripts/diag_recalibrate_directed.py`.
2. Regenerate the two pinned baselines:
   ```bash
   uv run python -c "
   from simulate import simulate; import numpy as np
   for cfg in (dict(N=2,K=1,P=1e-5,suf='n2_k1_t1000_seed0'),
               dict(N=10,K=4,P=0.2,suf='n10_k4_p02_t1000_seed0')):
       suf = cfg.pop('suf')
       G,s = simulate('LIF', tMax=1000, seed=0, fixed_dt_mode=False, **cfg)
       np.save('tests/baselines/lif_%s.npy' % suf,
               np.array(s.history['V']).T)
   "
   ```
3. `uv run pytest tests/` should be green.
4. `uv run python -m scripts.phase1_biophysics_report` — confirm rate
   in the 0.5–2 Hz/neuron band and ISI₅/ISI₁ ≥ 1.3. Commit if so.

## Decision point: fix B vs fix C vs hold

After fix A, the structural risks (#2 and #3 above) remain. Three
forward paths:

- **Hold.** Stop here. Repo is correct and tested. Publishable
  outcome: the methods paper (see below), plus maybe a Brief
  Communication off a failing pilot.
- **Fix B: up/down state dynamics.** 2–3 days engineering, ~30 LOC.
  Unlocks proposals #1 and #2 in their original framings. *This is
  the recommended path.*
- **Fix C: B + Snudda extraction + GRAPH-8 matching protocols.**
  2–3 weeks. Unlocks proposal #3. Has a six-month scoop clock from
  the Kotaleski lab.

## Per-proposal pilot success odds (rough, drawn from `DIAGNOSTICS.md`
and `RESEARCH_DIRECTIONS.md`)

| Proposal | Now (just fix A) | After fix B | After fix C |
|---|---|---|---|
| #1 AHP reservoir → Neural Comp 40–50 % | < 30 % | **65–75 %** | 65–75 % |
| #2 dt-as-observable → Front Neuroinform ~50 % | < 20 % | **50–60 %** | 50–60 % |
| #3 connectome atlas → Network Neurosci ~50 % | 50 % (no Snudda) | 50 % | **70–75 %** |

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

## Recommended sequencing

1. **Apply fix A immediately** (housekeeping).
2. **Spike fix B**: implement bistable Vm via a slow K inward
   rectifier (Wilson-Kawaguchi style). Run F7-style report. If
   bursty-but-sparse firing appears and the AHP-decay fit cleans up,
   commit. If the spike fails, fall back to the methods paper.
3. **In parallel with fix B coding**, draft the methods paper as a
   risk-free deliverable.
4. **After fix B lands**, run the proposal-#2 cheap pilot (it is
   the cheapest of the three pilots; existing scaffold lives at
   `scripts/proposal2_pilot.py`). 10 working days.
5. **Based on pilot #2 verdict**, commit to either proposal #1
   (LIF-het control week) or proposal #3 (Snudda spike) for the
   second paper.

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
