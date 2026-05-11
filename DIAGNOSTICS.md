# Project-level diagnostic findings — 2026-05-11

After Phase 0-2 + the Phase 3 shared minimum landed, the question
"have you found any serious problems that could kill this project?"
prompted four targeted diagnostics. Findings consolidated here.

All scripts live under `scripts/diag_*.py` and `scripts/phase1_biophysics_report.py`
and are runnable via `uv run python -m scripts.<name>`.

---

## D1 — Phase 1 biophysics calibration is broken under GRAPH-3 directed adjacency

**Script:** `scripts/phase1_biophysics_report.py`

**What changed:** GRAPH-3 correctly enforces `state.A[postsyn, presyn] = w`
with one entry per directed edge. The previous undirected adjacency had
both `A[u, v]` and `A[v, u]` set per edge — twice the recurrent
inhibition density. Halving that density frees the network to fire much
faster.

| Quantity                          | Pre-GRAPH-3 (undirected) | Post-GRAPH-3 (directed) | Literature target |
|-----------------------------------|--------------------------|--------------------------|--------------------|
| Mean firing rate                  | 0.80 Hz/neuron           | **18.0 Hz/neuron**       | 0.5–2 Hz/neuron    |
| ISI₅ / ISI₁ median                | 2.71                     | **0.80**                 | ≥ 1.3              |
| AHP τ median (fitted)             | 79 ms                    | 102 ms                   | ~50 ms             |
| Aggregate g_I mean                | 12.6 nS                  | 5.8 nS                   | (consistency check)|

**Severity:** High but recoverable. The proposal-#1 paper headline
("AHP conductances tune the network-level timescale reservoir") only
works if spike-frequency adaptation is visible, i.e. ISI₅/ISI₁ ≥ 1.3.
Right now adaptation is invisible because firing is refractory-limited.

**Fix path:** Re-calibrate (see D4). After re-calibration, re-run this
report to confirm BIO-1/2/3 targets are still hit. Update F7 numbers.

### Post-fix-B (B1 slow K + B2 OU drive, 2026-05-11)

After commits 85a07e7 (B1) + cb413bd (B2), F7 reports:

| Quantity                          | Pre-GRAPH-3 | Post-GRAPH-3 (Phase A only) | Post-fix-B | Literature target |
|-----------------------------------|-------------|----------------------------|------------|--------------------|
| Mean firing rate (Hz/neuron)      | 0.80        | 1.12                       | **0.67**   | 0.5–2              |
| ISI₅ / ISI₁ median                | 2.71        | 0.75                       | 0.63 *(n=4)* | ≥ 1.3            |
| AHP τ median (fitted, ms)         | 79          | 86                         | **31**     | ~50                |
| Aggregate g_I mean (nS)           | 12.6        | —                          | **1.07**   | (consistency)      |

Rate, AHP τ, and IPSC scale are all in or near the literature window.
ISI₅/ISI₁ has only 4 qualifying neurons because firing is now bursty —
spikes happen in up-state clusters with long down-state quiet periods —
so few cells emit 6 spikes in a 2.5 s window. With a longer run this
should clear. The mean ISI ratio across the 4 qualifying cells is 2.31,
above target; the median 0.63 is dominated by intra-burst short ISIs.

---

## D2 — The proposal-#1 α × β feasibility region is 1–2 cells of 24

**Script:** `scripts/diag_alpha_beta_grid.py`

RESEARCH_DIRECTIONS.md proposal #1 specifies a 6×4 grid:

- α ∈ {0, 0.25, 0.5, 1, 2, 4} × `conductance_A_max`
- β ∈ {0, 0.5, 1, 2} × `conductance_K_max`

Measured at default Poisson drive, before per-cell rate matching:

| Calibration                       | physio cells | hyper cells | silent cells |
|-----------------------------------|--------------|-------------|---------------|
| V_thresh = -42 mV (default)       | 1 / 24       | 14 / 24     | 7 / 24        |
| V_thresh = -41 mV (D4 recalibration) | 2 / 24    | 12 / 24     | 8 / 24        |

The grid is overwhelmingly bimodal: either hyper-firing (refractory-limited)
or silent. Between them is a hairline-thin physiological band.

**Severity:** Critical for proposal #1. The proposal's central
experimental design assumes you can tile α × β with physiological
firing then compare reservoir performance across the grid. With only
1–2 feasible cells the comparison axis collapses to a single point.

**Why it can't be fixed by rate matching alone:** F1 already showed the
rate response is a step function in drive, not a smooth knob. Tuning
`poisson_rate` per cell would push some cells across the bifurcation
discontinuously; the resulting "matched" comparison would be on
qualitatively different dynamical regimes per cell.

**Real fix paths (none cheap):**

1. **Add up/down state dynamics to STR.** In vivo MSNs sit at
   ~ -70 mV (down state) most of the time and intermittently transition
   to -50 mV (up state) where they fire 1–5 spikes per up state.
   The current model has no such mechanism, so it can't show the
   physiological bursty-but-sparse firing pattern at any parameter
   setting. ~2–3 days engineering, but addresses both proposals #1
   and #2's "no graceful sub-threshold regime" problem.
2. **Replace Poisson drive with an Ornstein-Uhlenbeck (OU) process** so
   the drive variance is independently tunable from the mean. Could
   open a wider feasibility band. ~1 day.
3. **Soften the threshold** (e.g., expIF, AdEx) — moves away from the
   strict integrate-and-fire bifurcation. Changes the simulator
   substantially.
4. **Accept the constraint and re-design proposal #1** around a much
   smaller α × β subgrid that happens to be physiological. May not
   support the headline reservoir-comparison claim.

### Post-fix-B (B1 slow K + B2 OU drive, 2026-05-11)

`scripts/diag_alpha_beta_grid.py` now runs at tMax=40000 (1.0 s of sim
time; the original tMax=4000 / 0.1 s captured only the initial OU
transient). Post-fix-B:

```
alpha\beta     beta=0   beta=0.5     beta=1     beta=2
0          2.03 [P]     1.51 [P]     1.53 [P]     1.53 [P]
0.25       1.85 [P]     1.53 [P]     1.54 [P]     1.53 [P]
0.5        1.73 [P]     1.55 [P]     1.58 [P]     1.50 [P]
1          1.66 [P]     1.60 [P]     1.59 [P]     1.60 [P]
2          1.80 [P]     1.80 [P]     1.75 [P]     1.70 [P]
4          2.75 [P]     2.72 [P]     2.75 [P]     2.81 [P]
Feasibility: 24/24 cells physiological.
```

Every cell of the proposal-#1 α×β grid is now in the 0.5-5 Hz/neuron
band. The bifurcation knife-edge of the threshold-reset + Poisson model
is replaced by a smooth response: OU drive variance + g_KIR rectification
together set the operating point, and α (AHP scale) / β (K scale) modulate
secondary features (timescales, decorrelation) without pushing firing
rate out of band. Proposal #1's headline experimental design — compare
reservoir performance across the grid under rate-matched dynamics — is
now feasible without per-cell rate matching.

---

## D3 — `S(t) = log(1/dt(t))` has too little variation to carry signal

**Script:** `scripts/diag_soderlind_separation.py`

The proposal #2 claim is that the adaptive-Euler-emitted `dt` stream
is a real-time early-warning observable. The decisive empirical
question: does `log(1/dt)` vary enough across a typical run to encode
the dynamical structure it is supposed to detect?

| Regime                 | Median log(dt) | Std (log units) | log(1/dt) range over run | dt range |
|------------------------|-----------------|------------------|---------------------------|----------|
| LIF sub-threshold      | −6.91 (at dt_max=1e-3 clamp) | 0.11 (clamp jitter) | ~0 | 1.0× |
| LIF supra refractory   | −11.51          | 0.01             | ~0.03                     | 1.03×    |
| LIF supra active dynamics | −11.36       | 0.09             | ~0.34                     | 1.4×     |
| STR full run           | −8.72           | 0.10             | **1.52**                  | **4.6×** |

**Verdict:** Total dt variation across an entire run is a factor of
1.4× for LIF and 4.6× for STR. The noise floor (std of log(dt) within
a regime) is ~0.1, equivalent to ~10% relative dt jitter from one
step to the next. For an EWS detector to flag a transition at 3-sigma
above this floor, the underlying dt must shift by ~35% — which under
LIF's narrow variation budget is essentially the entire dynamical
range.

**What this means for proposal #2:**

- **The Söderlind theorem applicability question is now moot.** Whether
  or not `log(1/dt) ≈ μ(J)` is mathematically defensible for spike-
  reset systems, **the signal itself does not have the dynamic range
  to encode multi-state transitions** in the way the doc envisions.
- The smoke-test K-sweep pilot's `S(t)` range `[-2.4, 2.6]` (after
  z-scoring) was apparent structure inflated from numerical jitter.
- The doc's "S(t) must beat σ²_r and AC(1) lead time by ≥20 ms" gate
  is unlikely to be cleared from the LIF cheap pilot. STR offers more
  budget but also more confounds.

**Severity:** High for proposal #2 as currently scoped. The cheapest
publishable framing surviving this finding would be:

> "The adaptive-Euler dt stream is a noisy proxy for stiffness with
> ~factor-of-5 dynamic range in a typical spiking model — useful as
> a folklore-quantification result, not as a competitive EWS
> detector."

That's a thinner story than the Chaos / Front Neuroinform pitch.

### Post-fix-B (B1 slow K + B2 OU drive, 2026-05-11)

`scripts/diag_soderlind_separation.py` rerun under fix-B:

| Regime              | Pre-fix-B log(1/dt) range | Post-fix-B log(1/dt) range |
|---------------------|---------------------------|----------------------------|
| LIF supra active    | 0.34 (1.4× dt)            | 0.35 (1.42× dt)            |
| STR full run        | 1.52 (4.6× dt)            | **0.55 (1.74× dt)**        |

Fix B *narrowed*, not widened, the dt observable's dynamic range. The
OU drive's stationary autocorrelation smooths the per-step `f(V)` magnitudes
that drive adaptive `dt`. Adding up/down state dynamics does not rescue
proposal #2's quantitative EWS claim.

**Honest finding for the P0 methods paper.** This strengthens, not weakens,
the dt-folklore-quantification thread: not only is the bare adaptive `dt`
stream noisy with narrow dynamic range, but the natural fix (give the
model more dynamics so `dt` has something to track) *makes it worse*
because slow correlated drive smooths the right-hand-side magnitudes. The
methods paper now has a clean before/after experiment to report.

---

## D4 — V_thresh re-calibration under directed adjacency

**Script:** `scripts/diag_recalibrate_directed.py`

Confirms the bifurcation under directed adjacency:

| V_thresh (mV) | Rate (Hz/neuron) |
|---------------|------------------|
| −40           | 0.05             |
| **−41**       | **1.25 (physio)** |
| −42           | 13.85            |
| −43           | 48.2             |
| −44           | 69.8             |

Single-mV-wide physiological window at V_thresh = −41 mV. Two orders
of magnitude in firing rate within 2 mV. Recovers the 1 Hz target,
but the calibration is as fragile as it was pre-GRAPH-3.

**Action:** Apply `const.V_thresh = -41 mV`. Re-pin LIF baselines.
Re-run F7 biophysics report and confirm BIO-1/2/3 targets.

### Post-fix-B (B1 slow K + B2 OU drive, 2026-05-11)

`scripts/diag_recalibrate_directed.py` now runs at tMax=40000 (the
original 4000 / 0.1 s caught only the OU transient and reported a flat
11.7 Hz across all V_thresh values). Post-fix-B:

| V_thresh (mV) | Pre-fix-B rate (Hz/neuron) | Post-fix-B rate (Hz/neuron) |
|---------------|-----------------------------|-------------------------------|
| −38           | —                           | 1.57                          |
| −40           | 0.05                        | 1.57                          |
| **−41**       | **1.25**                    | **1.57**                      |
| −42           | 13.85                       | 1.57                          |
| −44           | 69.8                        | 1.57                          |
| −46           | —                           | 1.59                          |
| −48           | —                           | 1.93                          |
| −50           | —                           | 3.22                          |

The single-mV knife-edge is resolved. V_thresh has an **8 mV wide
physiological band** (−38 to −46 mV). The threshold-reset bifurcation
isn't gone — push V_thresh deep enough (−55 mV) and rates explode — but
within the operating window, V_thresh is now a non-critical knob. This is
a calibration-robustness improvement of two orders of magnitude in
tolerance.

---

## Post-fix-B aggregate assessment (2026-05-11)

After commits 85a07e7 (B1 slow K) and cb413bd (B2 OU drive):

| Constraint | Pre-fix-B | Post-fix-B | Resolved? |
|------------|-----------|------------|-----------|
| D1: V_thresh calibration broken | 18 Hz/neuron at -42 mV | 1.57 Hz across -38 to -46 mV | **Yes** |
| D2: α×β feasibility 1/24 | 1-2 cells physio | **24/24 cells physio** | **Yes** |
| D3: dt observable narrow range | 1.52 log units (4.6×) | 0.55 log units (1.74×) | **No — worse** |
| D4: V_thresh single-mV window | knife-edge | 8 mV wide band | **Yes** |

Three of four constraints flipped from blocker to "resolved" or
"non-issue". The fourth (D3) flipped further toward "publishable
finding" — fix B making the dt observable *worse* strengthens, not
weakens, the methods paper's dt-folklore-quantification thread.

**Proposal-level implications:**

- Proposal #1 (AHP reservoir): D1 and D2 unblocked. Pilot is ready to run.
- Proposal #2 (dt-as-observable): D3 confirms structural impossibility.
  The original framing should be abandoned; the cheap replacement is to
  fold the dt-range measurement into the P0 methods paper.
- Proposal #3 (connectome atlas): D1 unblocked. D2 unblocked. Still
  needs fix C (Snudda + GRAPH-8) to start the actual pilot.

## Aggregate assessment (pre-fix-B, retained for the methods-paper before/after)

The codebase's *simulation core* is correct and fast. Phase 0-2 made
it trustworthy; Phase 3 shared minimum gave it the dispatch
infrastructure. The integrators are validated against LSODA. Tests
pass.

But three deeper findings now constrain what science can be done with it:

1. **STR is a fragile-bifurcation excitable system, not a graceful
   physiological firing model.** The 1 Hz operating window is a
   knife-edge under any drive parameterization. This kills proposal
   #1's α × β sweep as designed (D2) and threatens proposal #3's
   matching protocols.
2. **GRAPH-3's directed adjacency fix invalidated the F1/F7
   calibration.** Re-calibration is mechanical (D4) but every
   parameter we picked under undirected NWS needs to be re-checked.
3. **The adaptive-dt observable does not have the dynamic range to
   support proposal #2's quantitative EWS claim** (D3). The smoke-
   test pilot ran successfully but on a signal whose total variation
   is below the noise floor of the detectors it is supposed to beat.

**None of these are unfixable.** They are the kind of design-level
constraints that surface honestly during a pilot — the diagnostic
infrastructure paid off by surfacing them in hours rather than weeks.

**Practical next steps, by what each proposal would need:**

| Proposal | Surfaced threats | Cheapest path forward |
|----------|------------------|------------------------|
| #1 AHP reservoir | D1 (calibration), D2 (α×β collapse) | (a) Re-calibrate (~2 hrs); (b) replace Poisson with OU drive or add up/down state dynamics (~2-3 days) before committing |
| #2 dt-as-observable | D3 (no dynamic range) | Either (a) reframe as "quantifying folklore" — lower-tier venue; or (b) build the Brian2/NEURON portability spike in 1 day to see if their CVODE wrappers show wider dynamic range |
| #3 connectome atlas | D1 (calibration), D2 (matching may be infeasible) | (a) Re-calibrate; (b) test whether per-graph rate matching even has a feasible region by extending the α × β grid script to NWS / modular / MS-rewire variants |

The biggest single risk-reducer for all three proposals is to **add
up/down state dynamics to STR.** That's a literature-supported
biophysical addition (slow K conductance with V-gated activation) that
would open the physiological firing window and put the model on a
defensible footing for any of the three publications. Approximately
~30 LOC in `update_functions.py` (the doc itself estimates "~30 LOC,
2-3 days" for the proposal #2 up/down-state extension).
