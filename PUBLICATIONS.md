# Expected publication portfolio

A consolidated view of what papers come out of this project, what
each one claims, what's blocking it, and the realistic timeline.
Synthesizes `RESEARCH_DIRECTIONS.md` (the three proposals) with
`DIAGNOSTICS.md` (the methods-paper opportunity that emerged from the
diagnostic work).

Use this document to answer "what am I getting for the next 6/12/18
months of work?"

---

## Summary table

| # | Paper | Headline claim | Target venue | Acceptance odds | Status if fixes applied | Time to manuscript |
|---|---|---|---|---|---|---|
| **P0** | **Methods: bifurcation infeasibility + dt folklore quantification + a fix-B before/after** | Threshold-reset spiking-network sweeps have intrinsic infeasibility regions that biophysical bistability removes; the adaptive-dt observable's dynamic range is narrower than folklore suggests and *narrows further* once the model is made more biophysically realistic. | Front Comp Neurosci (Methods) / PLOS Comp Bio (Methods) | **55–65 %** (up from 50–60 %; before/after structure strengthens the methods angle) | **Publishable as-is from current repo.** All four diagnostic findings (D1 resolved, D2 resolved, D3 honestly worsened, D4 resolved) have pre/post-fix-B numbers in `DIAGNOSTICS.md`. | ~2 weeks |
| **P1** | **AHP conductances as a network-level timescale reservoir** | Biophysical AHP + voltage-gated K jointly produce a broader per-neuron timescale distribution and higher Jaeger memory capacity than any rate-matched LIF variant (including LIF-het and LIF-ALIF). | Neural Computation | 40–50 % primary; 60–70 % at Front Comp Neuro fallback | **Fix B landed (24/24 α×β cells feasible).** Still needs: LIF-het, LIF-ALIF, rate-matching, ANA-5 reservoir benchmark, ANA-6 IPC decomposition. | 4–6 months |
| **P2** | ~~dt(t) as a free real-time dynamical observable for EWS~~ | — | — | **Abandoned.** D3 confirmed structurally; fix B narrowed STR `log(1/dt)` range from 1.52 to 0.55. Salvage as P0 component. | — |
| **P3** | **Necessary structural features for striatal dynamics: a null-model atlas** | A feature-by-signature necessity matrix for striatal dynamics across 5 graph nulls (NWS, Snudda, MS-rewire, Gamma-kernel, modular). | Network Neuroscience | ~50 % primary; ~25 % at eLife / PLOS Comp Bio fallback | Needs **fix C** (GRAPH-4 Snudda + GRAPH-8 matching protocols). Six-month scoop clock from the Kotaleski lab. | 5–6 months |

---

## P0 — Methods: bifurcation infeasibility + dt folklore quantification

**One-sentence claim:** "Spiking-network parameter sweeps in
threshold-reset models have intrinsic bifurcation-induced
infeasibility regions that confound rate-matched comparisons, and the
free `dt(t)` stream from adaptive solvers — sometimes cited as an
implicit dynamical observable — has a measurable and quite narrow
dynamic range that constrains its utility as an early-warning signal."

**Why it's publishable:**

- Cites Söderlind/Jay/Calvo 2015 and Scheffel 2024 as predecessors who
  framed dt-as-stiffness-indicator on single ODEs; the contribution
  here is the spiking-network measurement and the calibration cookbook.
- Reusable diagnostic scripts that any spiking-reservoir paper should
  run before claiming a parameter sweep is meaningful.
- Aligns with the methods-paper precedent at Front Comp Neurosci
  (e.g., reservoir-validation cookbooks).

**What's already in the repo:**

- `scripts/diag_alpha_beta_grid.py` — feasibility before/after fix B
  (1/24 → 24/24 cells physiological)
- `scripts/diag_recalibrate_directed.py` — V_thresh window before/after
  fix B (single mV → 8 mV wide)
- `scripts/diag_soderlind_separation.py` — dt-range before/after fix B
  (1.52 → 0.55 log units; honest finding)
- `scripts/phase1_biophysics_report.py` — BIO-1/2/3 + AHP τ pre/post
- `DIAGNOSTICS.md` — synthesis with post-fix-B sections under each of
  D1, D2, D3, D4 and a clean aggregate before/after table
- `data/p0/*.txt` — raw stdout dumps from each diagnostic, for direct
  citation in the manuscript

**What's still needed:**

- ~2-3 weeks of writing.
- Manuscript drafting against the following outline:

  | Section | Source material | Status |
  |---|---|---|
  | Intro: Söderlind/Scheffel framing | `RESEARCH_DIRECTIONS.md` §Proposal 2 citations | Outline only |
  | Methods: model + dispatched graphs | `CLAUDE.md`, `state.py`, `graph_build.py`, `integrators.py` | All code present |
  | Result 1: Bifurcation infeasibility regions | `figures/p0/alpha_beta_heatmap.{png,svg}`, `data/p0/alpha_beta_grid_{pre,post}.csv`, DIAGNOSTICS.md D2 | Figures and CSVs generated |
  | Result 2: V_thresh sensitivity knife-edge | `figures/p0/v_thresh_sensitivity.{png,svg}`, `data/p0/v_thresh_sweep_{pre,post}.csv`, DIAGNOSTICS.md D4 | Figures and CSVs generated |
  | Result 3: Bistability rescues α×β grid | `figures/p0/v_histogram.{png,svg}`, `data/p0/v_histogram_post.csv` | Figures and CSVs generated |
  | Result 4: dt-folklore quantification | `figures/p0/dt_kde.{png,svg}`, `data/p0/dt_ranges.csv`, DIAGNOSTICS.md D3 | Figures and CSVs generated |
  | Calibration cookbook | `scripts/phase1_biophysics_report.py`, `scripts/diag_recalibrate_directed.py` | Scripts present |
  | Discussion: generalization | `scripts/p0_brian2_portability.py` (optional) | Not yet implemented; ~3 days extra |
  | Reproducibility | `scripts/p0_make_figures.py` (single-entry rebuild) | Done |
- Optional Brian2/NEURON portability spike (P0.4) for the "does this
  generalize" reviewer defense. Skip if calendar pressure.

**Falsification:** None — this is a measurement paper, not a hypothesis
test.

**Risk:** Low. Reviewer might ask "but does this generalize beyond
NeuroRC?" — defense is to add a Brian2 / NEURON CVODE comparison spike
(~3 days extra work).

---

## P1 — AHP reservoir (`RESEARCH_DIRECTIONS.md` §Proposal 1)

**One-sentence claim:** "In a fixed small-world reservoir, biophysical
AHP and voltage-gated potassium conductances jointly produce a broader
per-neuron autocorrelation-timescale distribution and higher Jaeger
memory capacity than any rate-matched LIF reservoir — including LIF
with a tuned per-neuron leak distribution — establishing biophysical
adaptation as the network-level mechanism for the timescale reservoir
originally described in single neurons by Bernacchia et al. (2011)."

**Falsification criterion (from doc):** If LIF-het matches STR on MC
within 20 %, OR if the per-neuron τᵢ distribution from STR is not
visibly broader than from LIF-het, the paper does not exist. Pivot to
a τᵢ-shape-only claim or abandon.

**Engineering prerequisites:**

- ~~Fix A: V_thresh recalibration~~ — done (commit 863faf8).
- ~~Fix B: up/down state dynamics~~ — done (commits 85a07e7, cb413bd).
  α×β grid 24/24 feasible.
- **Still required:**
  - LIF-het (per-neuron g_L) and LIF-ALIF (adaptive threshold) variants.
  - Firing-rate matching (binary search on drive — or, given fix B has
    rates uniform across the grid without matching, may be unnecessary).
  - `metrics/pipeline_a_reservoir.py` (ridge regression + LOO-CV + MC +
    NARMA-10 + IPC decomposition).
  - `metrics/ipc.py` (Dambre 2012 reimplementation) — heaviest single
    piece of new code. 3–5 days alone.

**Top threats:**

1. LIF-het matches STR (doc estimates 30 % likely; Perez-Nieves 2021 is
   the real adversary).
2. Rate-matching fails across α × β. Already partly observed in D2 —
   fix B should fix this.
3. Scoop from Goodman or Salaj/Maass labs in 6 months.

**Time:** ~4–6 months from fix B to manuscript.

---

## P2 — dt-as-observable — ABANDONED (post fix-B)

**Status:** Original framing abandoned after fix B narrowed STR
`log(1/dt)` range from 1.52 to 0.55 log units. The intuition that
biophysical bistability would *expand* the dt observable's dynamic
range was wrong: OU drive's slow correlated noise smooths
right-hand-side magnitudes, reducing the spread of adaptive `dt`.

**Salvage path:** Fold the dt-range measurement (pre/post-fix-B) into
the P0 methods paper under the "dt folklore quantification" thread.
The before/after structure is actually *stronger* there than a
positive result would have been: "we hypothesized fix B would widen
S(t); it narrowed S(t); here's the data; conclude the dt-observable
folklore is not just narrow in scope but anti-correlated with model
realism."

**What was already in the repo (still useful for P0):**

- `metrics/ews.py`, `metrics/oracles.py`, `metrics/stats.py`
- `scripts/proposal2_pilot_smoke.py`
- `scripts/proposal2_pilot.py`
- `scripts/diag_soderlind_separation.py` — the decisive test

---

## P3 — Connectome atlas (`RESEARCH_DIRECTIONS.md` §Proposal 3)

**One-sentence claim:** "By running identical biophysical dynamics on
five carefully matched graph nulls — including a Snudda-derived MSN
subgraph and its degree-preserving rewire — we produce the first
feature-by-signature necessity matrix for striatal dynamics,
transferring the Gal/Reimann/Markram 2020 cortical framework to the
basal ganglia and answering the question Carannante 2024 explicitly
left open."

**Falsification criterion (from doc):** Cliff's δ < 0.8 between NWS
and Snudda dwell-time distributions in the pilot → publish as Brief
Communication ("Striatal assembly switching is robust to connectivity
topology") and stop. Either branch publishes.

**Engineering prerequisites:**

- Fix A.
- Fix B.
- GRAPH-4: Snudda Docker pipeline + extraction script. Pinned to the
  FrontNeuralCircuits2021 tag, 4+ years old. ~3–5 days of HDF5
  schema-drift work.
- GRAPH-6: Gamma kernel — blocked on Yim 2017 parameter verification.
- GRAPH-8: four matching protocols (rate, E-drive, I-drive, variance).
- `metrics/pipeline_c_spikes.py`: NMF assembly detection, Pareto ISI
  fitting, Plenz-style avalanche-modulated drive, Clauset power-law
  fit.

**Top threats:**

1. Kotaleski-lab releases Carannante-dynamics extension in 6 months
   (~30 %). Mitigation: speed, early email to Hjorth/Kotaleski.
2. NWS vs Snudda dwell-time distributions don't differ. Mitigation:
   already a Brief Communication fallback.
3. Snudda extraction infeasible in time. Mitigation: fall back to
   synthetic distance-dependent calibrated to Hjorth 2020 connection
   probabilities (Belić 2024's approach).

**Time:** ~5–6 months from fix C to manuscript.

---

## Realistic expected portfolio by commitment level

Updated post fix-B: P2 abandoned, P1 prereqs satisfied (still needs
LIF-het + reservoir pipelines), P0 strengthened by before/after structure.

| Commitment | Expected papers | Composition |
|---|---|---|
| ~~Ship what's done (no fixes)~~ | n/a | (fixes A+B already landed) |
| **Ship current state (P0 only)** (~2-3 weeks writing) | **1** | P0; methods paper has full before/after structure |
| **P0 + P1 pilot in parallel** (P0 ~3 wks, P1 ~5 mo) | **1.5–2** | P0 + P1 if pilot survives. P3 deferred. |
| **P0 + fix C + P3** (~3 wks engineering, then 5-6 mo) | **2** | P0 + P3 (high-prestige, longer path) |
| **Full plan** (~12 months) | **2-3** | P0 + P1 + P3 |

P0 is the *floor*: it survives no matter what happens with the main
pilots. It exists because the diagnostic work — done as defensive due
diligence on the three main proposals — surfaced a publishable result
of its own.

---

## Decision shorthand (post fix-B)

- **Lowest-risk single-paper bet:** Write P0 from current state. ~2-3
  weeks, no further engineering.
- **Best risk-adjusted return:** P0 first, then commit to P1 pilot
  (fix B already landed). ~5 months for two papers.
- **Highest ceiling:** P0 + fix C + P3 + P1. 12-18 months for 3 papers.

See `NEXT_STEPS.md` for the current state and recommended sequencing.
