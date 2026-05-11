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
| **P0** | **Methods: bifurcation infeasibility + dt folklore quantification** | Threshold-reset spiking-network sweeps have intrinsic infeasibility regions; the adaptive-dt observable's dynamic range can be measured and is much narrower than folklore suggests. | Front Comp Neurosci (Methods) / PLOS Comp Bio (Methods) | 50–60 % | **Publishable as-is from current repo.** No further fixes needed; everything reportable is in `DIAGNOSTICS.md` + `scripts/diag_*.py`. | ~2 weeks |
| **P1** | **AHP conductances as a network-level timescale reservoir** | Biophysical AHP + voltage-gated K jointly produce a broader per-neuron timescale distribution and higher Jaeger memory capacity than any rate-matched LIF variant (including LIF-het and LIF-ALIF). | Neural Computation | 40–50 % primary; 60–70 % at Front Comp Neuro fallback | Needs **fix B** (up/down state dynamics in STR). After that: LIF-het, LIF-ALIF, rate-matching, ANA-5 reservoir benchmark, ANA-6 IPC decomposition. | 4–6 months |
| **P2** | **dt(t) as a free real-time dynamical observable for EWS** | The adaptive-solver `dt` stream detects synchronization onset, E/I-balance breakdown, and up/down bistability earlier and with higher SNR than the standard EWS toolbox at no extra compute cost. | Chaos (AIP) primary; Front Neuroinform fallback | 35 % primary; 50 % fallback | Needs **fix B**. After fix B, `S(t)` gets the orders-of-magnitude dynamic range it currently lacks. Then: refine pilot's experimental design (D3 follow-up), ANA-7 baseline detectors. | 3–4 months |
| **P3** | **Necessary structural features for striatal dynamics: a null-model atlas** | A feature-by-signature necessity matrix for striatal dynamics across 5 graph nulls (NWS, Snudda, MS-rewire, Gamma-kernel, modular). | Network Neuroscience | ~50 % primary; ~25 % at eLife / PLOS Comp Bio fallback | Needs **fix C** (B + GRAPH-4 Snudda + GRAPH-8 matching protocols). Six-month scoop clock from the Kotaleski lab. | 5–6 months |

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

- `scripts/diag_alpha_beta_grid.py` — the 1-of-24 feasibility finding
- `scripts/diag_recalibrate_directed.py` — V_thresh single-mV-window
- `scripts/diag_soderlind_separation.py` — dt-range budget for LIF / STR
- `DIAGNOSTICS.md` — synthesis with citations

**What's still needed:**

- ~2 weeks of writing
- Additional figures: dt distribution kernel-density plots, α × β heatmap

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

- Fix A: V_thresh recalibration — restores Phase 1 firing target.
- Fix B: up/down state dynamics — opens the α × β grid that the
  proposal needs.
- New code: LIF-het (per-neuron g_L), LIF-ALIF (adaptive threshold),
  firing-rate matching (binary search on drive), `metrics/`
  pipeline_a_reservoir.py (ridge regression + LOO-CV + MC + NARMA-10
  + IPC decomposition).
- `metrics/ipc.py` (Dambre 2012 reimplementation) — the heaviest
  single piece of new code in the whole project. 3–5 days alone.

**Top threats:**

1. LIF-het matches STR (doc estimates 30 % likely; Perez-Nieves 2021 is
   the real adversary).
2. Rate-matching fails across α × β. Already partly observed in D2 —
   fix B should fix this.
3. Scoop from Goodman or Salaj/Maass labs in 6 months.

**Time:** ~4–6 months from fix B to manuscript.

---

## P2 — dt-as-observable (`RESEARCH_DIRECTIONS.md` §Proposal 2)

**One-sentence claim:** "The variable timestep stream that every
adaptive ODE solver already emits is a free, network-level
finite-time-Lyapunov proxy, and on coupled spiking neurons it detects
E/I-balance breakdown and synchronization onset earlier and with
higher SNR than the standard early-warning toolbox (variance, lag-1
autocorrelation, spectral entropy) — at no extra compute cost."

**Falsification criterion (from doc):** S(t) must beat *both* σ²_r and
AC(1) in mean lead-time at 5 % FPR by ≥ 20 ms (Wilcoxon p < 0.05) in
the cheap pilot. If not, abandon.

**Engineering prerequisites:**

- Fix A.
- Fix B (the key one — gives `S(t)` orders-of-magnitude dynamic range
  via down-state quiescence vs up-state bursting).
- Refine pilot experimental design: longer sims, smarter
  transition oracle (R-dwell threshold relaxation, non-zero-variance
  baseline window for FPR calibration). All issues are documented in
  the `scripts/proposal2_pilot.py` commit message.

**What's already in the repo:**

- `metrics/ews.py`, `metrics/oracles.py`, `metrics/stats.py` — all
  baseline detectors + Kuramoto oracle + lead-time stats.
- `scripts/proposal2_pilot_smoke.py` — end-to-end smoke test passes.
- `scripts/proposal2_pilot.py` — reduced K-sweep scaffold (5 × 3,
  ~32 s wall).

**Top threats:**

1. Even after fix B, `S(t)` might not beat AC(1) (doc estimates 30 %
   abandon probability).
2. "This is folklore" reviewer objection. The P0 methods paper actually
   *helps* P2 here by separately quantifying what the folklore reach is.
3. Scoop from CFD/N-body — ShockCast 2025 shows the field is moving.

**Time:** ~3–4 months from fix B to manuscript. *Cheapest of the three
main pilots.*

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

| Commitment | Expected papers | Composition |
|---|---|---|
| **Ship what's done** (no fixes) | 0–1 | P0 only, if you write it |
| **Fix A only** (~2 hrs) | 0.5–1 | P0 + likely Brief Communication off a failing pilot |
| **Fix A + B** (~1 week incl. fix A) | **1.5–2** | P0 + one of {P1, P2}; P2 is cheapest |
| **Fix A + B + run pilots in parallel** (6 weeks to verdict) | **2** | P0 + 1 of {P1, P2} surviving its pilot. P3 deferred. |
| **Fix A + B + C** (~3 weeks then 6+ months) | **2.5–3** | P0 + P2 (cheap, short) + P1 or P3 (high-prestige, long) |
| **Full plan** (12+ months) | 3 | P0 + P1 + P3, with P2 as Brief Communication if it survives pilot |

P0 is the *floor*: it survives no matter what happens with the main
pilots. It exists because the diagnostic work — done as defensive due
diligence on the three main proposals — surfaced a publishable result
of its own.

---

## Decision shorthand

- **Lowest-risk single-paper bet:** Fix A only → write P0 → ship.
  Total time: ~3 weeks.
- **Best risk-adjusted return:** Fix B → run P2 pilot → P2 + P0 in
  parallel. Total time: ~5 months for two papers.
- **Highest ceiling:** Fix C → all three main proposals + P0. Total
  time: 12–18 months for 2–3 main papers + the methods floor.

See `NEXT_STEPS.md` for the immediate next actions to take regardless
of which path you pick.
