# NeuroRC — Implementation Audit & Action Plan

A compiled report of five focused implementation reviews covering the shared infrastructure work needed before any of the three planned papers (proposals #1 AHP reservoir, #2 dt-as-instrument, #3 connectome atlas — see `RESEARCH_DIRECTIONS.md`).

Five independent agents reviewed: (1) STR biophysical realism vs published striatal MSN models, (2) numerical integration and delay handling, (3) vectorization and GPU acceleration, (4) graph generation algorithms, (5) reservoir-computing and spike-train analysis methodology.

This document is the operational counterpart to `RESEARCH_DIRECTIONS.md`. That document answers "what should we publish?"; this one answers "what must be fixed before we can publish anything?"

---

## Executive summary

**The codebase contains several real bugs in multiple files.** The original Week 0 plan in `RESEARCH_DIRECTIONS.md` (~5 items, ~1 week) was too optimistic; the honest pre-pilot foundation work is closer to **2-3 weeks**, broken into a pre-flight pass (bug fixes that block running on a modern Python stack), a biophysics + numerics refactor, and an analysis-infrastructure setup. Several of the bugs were independently flagged by multiple agents from different angles, which is high signal.

Three structural decisions must be made before any code changes:

1. **STR spike-reset policy:** subthreshold-continuous (Pyle & Rosenbaum 2019 style, fine for #1) vs. proper threshold-reset (required for #3 Ponzi-Wickens / Plenz signatures). Pick one. Document in code.
2. **Integrator branching:** fixed-dt (Heun + exp-Euler, Δt=25 µs) for proposals #1 and #3; adaptive-dt (current scheme) for proposal #2. Single Boolean flag in `const.py`. The two cannot share without invalidating one experiment.
3. **STR biophysics calibration:** the current AHP time constant τ_A = 1 ms (not 50 ms as assumed by the proposal #1 framing) is the most consequential single bug. Until fixed, the "AHP timescale bank" claim is structurally dead.

---

## Confirmed bugs — cross-agent table

| # | Bug | File | Severity | Flagged by |
|---|---|---|---|---|
| 1 | `_a_A = 1e3` gives τ_AHP = 1 ms (should be ~20/s → τ ≈ 50 ms, matching Nisenbaum & Wilson 1995, Wolf et al. 2005) | `const.py:10` | **Kills proposal #1's headline claim** | Biophysics, Integration |
| 2 | `w_A = 0.01` × `g_A_max = 25 nS` = 0.25 nS AHP ceiling, ~1% of leak — effectively neutralizes adaptation | `const.py:29` | **Kills proposal #1** | Biophysics |
| 3 | `g_K_max` (25 nS, voltage-gated K saturation conductance) used as scale for recurrent inhibitory input — almost certainly a copy-paste bug; should be a proper `g_I_max ≈ 1.5 nS` (Koos/Tepper/Wilson 2004) | `update_functions.py:91` | High biophysical implausibility | Biophysics |
| 4 | `weight_generator.py` hardwires every weight to 1, despite documented uniform-distribution range in `const.py` (lowrand/highrand are dead) and a dead `getWeight()` function | `weight_generator.py:13` | **Until fixed, no graph comparison means anything** | Biophysics, Vectorization, Graph |
| 5 | 4× `print` calls in `delay()` execute every timestep, capping throughput at ~10⁴ steps/sec | `math_functions.py:49-52` | High; free 10× speedup by removing | Vectorization |
| 6 | `random.uniform(1, 10000)` (a float) passed as `seed=` to NetworkX — modern NetworkX requires int seed | `graph_build.py:8` | **Will throw on modern NetworkX** | Vectorization |
| 7 | NetworkX 1.x API (`G.node[j]`) used everywhere except `run.py:98` which uses 2.x (`G.nodes[1]`) | `update_functions.py`, `graph_build.py` | **Won't run on modern NetworkX** | Vectorization, Analysis |
| 8 | `graph_build.set_graph_attributes` resets conductances to 0, ignoring `const.py` init values (`g_*_init = 10 nS`) — 50-100 ms artifactual transient before any analysis can start | `graph_build.py:20-22` | Medium | Biophysics |
| 9 | `const.dt_list` is a module-level global; accumulates across runs in the same Python process — silently corrupts multi-seed batches | `const.py:39` | **Will silently invalidate sweeps** | Analysis |
| 10 | Per-node voltage stored as Python list with `.append()` each step; at N=500, T=30 s, dt̄=1e-5 → ~96 GB memory | `graph_build.py:23,29` | **Cannot run any proposal at scale** | Integration, Vectorization |
| 11 | Constant cortical drive `I = 1e-3` identical across all neurons; produces phase-locked initial transients with no input-driven decorrelation | `const.py:30`, `update_functions.py:84` | High; reservoir & population analyses require time-varying input | Biophysics |
| 12 | σ slope `k = β = 0.8/V` is effectively linear over the dynamic range; comment `(V)^-1` may be wrong by 3 orders (intended ~800/V or higher) | `const.py:25,28` | Medium; check against Wilson & Kawaguchi 1996 | Biophysics |
| 13 | Adaptive dt produces non-uniform time grid — incompatible with FFT, autocorrelation, Hilbert transform, avalanche binning. All frequency-domain analyses biased without resampling | architectural | High | Integration, Analysis |
| 14 | `delay()` snaps backward to the smallest step where cumulative dt ≥ τ_D — systematic snap-up bias; under adaptive dt the delay resolution co-varies with dt itself | `math_functions.py:39-53` | Critical confound for proposal #2 (log(1/dt) and delay precision are perfectly anticorrelated by construction) | Integration |
| 15 | No spike extraction layer (no threshold detector, no refractory enforcement) | architectural | Required for proposal #3 | Analysis |

---

## Decision 1 — STR spike-reset policy

The current code has no spike reset (the `if V > 0.04` line is commented out). The model is *de facto* a continuous voltage-conductance dynamical system whose only "firing" is graded σ(V). This is the worst of both worlds: it looks like a spiking model (g_E, g_I, g_K, reversal potentials) but reviewers will assume it spikes and call it broken when they see no reset.

You must pick one and commit:

### Option A — declare subthreshold-continuous (recommended for #1 only)
- Cite Pyle & Rosenbaum (2019, *Neural Computation* 31:1430) for the precedent: graded rate-like striatal reservoir without spikes.
- Cite Sussillo & Abbott (2009, *Neuron* 63:544) for the broader rate-RNN reservoir tradition.
- Document in `update_functions.py` and never use the word "spike."
- Frame σ(V) as a synaptic-release nonlinearity, not a spike rate.
- LIF model needs matching treatment.

### Option B — add proper threshold-reset (required for #3)
- Threshold detector at V_thresh; brief depolarization or delta event into downstream g_I; reset V to V_reset = V_L; refractory ~2 ms.
- Required for ISI distributions, CV_ISI, Fano factors, Ponzi-Wickens assembly switching, Petermann-Plenz avalanche analysis — **half of proposal #3's target signatures are uncomputable without spikes.**

**Recommendation:** option B is the only one compatible with all three proposals. Implement once for both STR and LIF; document the choice in `update_functions.py`.

---

## Decision 2 — Integrator branching

Three proposals make incompatible demands. Resolve by branching:

| Proposal | Integrator | Why |
|---|---|---|
| #1 AHP reservoir | **Fixed-dt Heun (RK2) for V + exp-Euler for conductances**, Δt = 25 µs | Fair STR-vs-LIF requires identical time grid. Exp-Euler is exact for the linear conductance equations. Heun is 2nd-order on the nonlinear V equation. Stewart & Bair 2009; Brette et al. 2007 §3.2; Brian2's `exponential_euler` for precedent. |
| #2 dt-as-instrument | **Keep current adaptive dt = ε/max|f| exactly as-is** | The integrator's chosen dt IS the experiment. Replacing it invalidates the framing. |
| #3 connectome atlas | **Fixed-dt same as #1**, with optional `dt_floor` for hub stability under heavy-tailed Snudda subgraphs | Cross-graph comparison must be hermetic. Adaptive dt collapses on hub firings. |

Implementation: Boolean `fixed_dt_mode` in `const.py` (default True); when False, current adaptive rule runs. Add `dt_floor` param (default 25 µs) for safety even under adaptive mode.

**Critical for proposal #2's framing:** `S(t) = log(1/dt)` reduces to `log max_j |f_v,j(t)|` plus a constant — the conductance state magnitudes (~10⁻⁵) are negligible vs voltage RHS (~2-2000 V/s). The proposal #2 theory must respect this: dt-as-observable is a voltage-only observable. The conductance state is along for the ride.

---

## Decision 3 — STR biophysics calibration

Without these fixes, the STR model is closer to a broken LIF than to a striatal MSN. Three are critical for proposal #1, several more for proposal #3.

### Must fix (block all three proposals)

| Param | Current | Target | Reference |
|---|---|---|---|
| `_a_A` (AHP inverse time constant) | 1000/s → τ=1 ms | **20/s → τ=50 ms** | Nisenbaum & Wilson 1995; Wolf et al. 2005 (τ_SK ≈ 80 ms) |
| `w_A` (AHP scale) | 0.01 → 0.25 nS ceiling | **0.5 (or reduce g_A_max to 1 nS)** | Wolf 2005 g_SK ≈ 0.5-2 nS |
| Recurrent inhibition scale at `update_functions.py:91` | `g_K_max` (25 nS) | **New `g_I_max ≈ 1.5 nS`** as separate constant | Koos/Tepper/Wilson 2004 unitary IPSCs |
| Cortical drive | Constant `I = 1e-3` | **Poisson kicks** event-driven | Stern/Jaeger/Wilson 1998 |
| Spike reset | Disabled | **Option B (threshold-reset)** | Required for proposal #3 |
| σ slope `k`, `β` | 0.8/V (effectively linear) | **Verify intended value; likely 80-800/V** | Wilson & Kawaguchi 1996; check units |

### Should fix (before proposal #3 specifically)

| Param | Action | Reference |
|---|---|---|
| K_IR (inward rectifier K⁺) | **Add** as `(V_K - V) · g_KIR · h_KIR(V)` with sigmoid centered at -80 mV, slope ~5/mV, g_KIR ~10-15 nS | Steephen & Manchanda 2009; Wilson & Kawaguchi 1996 |
| D1/D2 node attribute | **Add** as boolean on each node; trivial | For proposal #3 modular-D1/D2 graph |
| Init conductances | Honor `const.py` values; remove the zero-reset in `graph_build.py:20-22` | — |

### Optional (nice-to-have)

- NMDA with voltage-dependent Mg block: Wolf 2005 made this the centerpiece for up-state stabilization. Required only if discussing up/down states.
- Per-neuron `g_L` heterogeneity for STR (matching the LIF-het control in proposal #1).

### Leave alone

- Full HH sodium kinetics (use threshold-reset instead).
- Multi-compartment geometry (that's Snudda's territory).
- Calcium dynamics, plasticity, dopamine D1/D2 receptors (out of scope).
- FSI, ChIN, LTS interneurons (cite Hjorth 2020 / Carannante 2024 and refuse — framing is MSN-MSN only).

---

## Numerical & integration recommendations

### Architecture
- **State as flat NumPy arrays**, not NetworkX node attributes. Refactor `graph_build.set_graph_attributes` to return numpy state arrays; graph stays a connectivity object only.
- **Ring buffer for delays** indexed by `int(τ_D / Δt)` under fixed dt; linear interpolation under adaptive dt (required for proposal #2 to be defensible).
- **Recurrent input via sparse SpMV:** `g_I_recurrent = A.dot(sigma(V_delayed))` using `scipy.sparse.csr_matrix`. 100-500× speedup over current loop.

### Integrator details
- **Heun (RK2)** on voltage equation: predict V* = V + Δt·f(V); correct V_new = V + 0.5·Δt·(f(V) + f(V*)).
- **Exponential Euler** for each conductance: `g_new = g·exp(-a·Δt) + (s/a)·(1 − exp(-a·Δt))`. Exact for the linear part.
- **Δt = 25 µs** for both STR and LIF; matched-grid is the whole point.
- **Do NOT use `scipy.integrate.solve_ivp`** for production runs — the per-step Python callback overhead at N=500 will kill performance. A hand-rolled vectorized Heun in ~30 lines outperforms it 50-100×. Use solve_ivp only for the RK45 cross-check reference run in proposal #2.

### Adaptive-dt confounds for proposal #2
The `dt = ε/max|f|` rule has known failure modes that must be controlled:
1. **Single-neuron domination** — `max(M)` reduces over the population; one neuron's transient sets the global dt. This is "loudest neuron observable" not "network observable." Required controls: per-neuron dt_j, 50-node subsample max, 95th-percentile dt.
2. **Quiescent-network divergence** — when all f→0, dt→∞. Cap with `dt_max` to prevent step-past events.
3. **Conductance equations contribute nothing** to max|f|. S(t) measures voltage RHS only.
4. **Delay-precision artifact** — `log(1/dt)` and the precision of `delay()` are perfectly anticorrelated under adaptive dt. Implement linear interpolation in delay() to break this confound.
5. **Validate against RK45** with `scipy.integrate.solve_ivp(method='RK45', rtol=1e-6, atol=1e-9)` as cross-check; require ρ(S_current, S_RK45) > 0.9.

---

## Vectorization & performance

### Per-step cost (current code)
~4 ms/step at N=500 single-core; with the `print`s in `delay()`, ~40 ms/step. At N=10k: ~80 ms/step + 96 GB memory.

### Recommended baseline upgrade (1 week, 100-300× speedup)
- NumPy state vectors + `scipy.sparse.csr_matrix` adjacency + SpMV for recurrent input
- Ring buffer for delays
- Fixed dt
- Remove `print` calls
- `joblib.Parallel(n_jobs=-1)` for sweep parallelism

Proposal #1's 7700 runs becomes ~1 day on 16 cores.

### Per-proposal framework recommendation

| Proposal | Primary stack | Fallback / extension |
|---|---|---|
| #1 AHP reservoir | NumPy + scipy.sparse + joblib + reservoirpy | JAX with vmap on GPU for batched seeds (10-50× more) |
| #2 dt-as-instrument | NumPy + scipy.sparse + keep adaptive dt + h5py logging | scipy.integrate.solve_ivp for RK45 cross-check rig |
| #3 connectome atlas | Brian2 with `cpp_standalone` (cleanest for many connectomes) | Brian2CUDA if pushing to N≥10k; Snakemake for sweep management |

### One-framework-for-all option
**JAX.** Autodiff is genuinely useful for proposal #1 (Lyapunov spectra, observability gramians); `vmap` handles sweeps; fixed-dt within `lax.scan` is straightforward. Cost: 4-8 days learning curve, functional-update requirement (no in-place mutation).

### GPU?
At N=500 a single sim doesn't benefit much. **At the sweep level (7700 sims for proposal #1, 6000 for proposal #3) batched on GPU via `vmap`: A100 finishes proposal #1 in ~2-6 hours instead of 1 day on 16 CPU.** RTX 4090 or M-series GPU is enough. Don't write CUDA by hand.

### Memory
- Flat NumPy arrays for state, `float32` for history.
- Ring buffer size = `max_delay / Δt + safety`; for D≈100, N=500 that's 50k floats vs 5M.
- HDF5 or Zarr for long sweeps; lzf compression ~3× reduction.
- Stream-to-disk during sweeps; don't accumulate 7700 voltage histories in RAM.

---

## Graph generation

### Per-graph spec table

| Graph | Library / function | Parameters | LOC |
|---|---|---|---|
| NWS | `nx.newman_watts_strogatz_graph` → directed via random orientation | n=500, k ∈ {8, 16, 32} bracket Snudda mean degree, p=0.01; verify K is even | ~10 |
| Snudda-MSN | h5py read of `network/synapses` + cell-type mask + contiguous subvolume | ~200 µm cube → ~500 MSNs (Oorschot 1996: ~85k/mm³); preserve D1/D2 attribute | ~60 |
| MS-rewire | `nx.directed_edge_swap` for binary; Rubinov-Sporns 2011 or Hanson 2024 for weighted | `nswap=100·|E|` (NOT 10·|E| — too few for clustered graphs); verify clustering plateau | ~25 |
| Gamma kernel | Custom: uniform positions in cube; P(d) ∝ d^(k-1)·exp(-d/θ); Bernoulli | **Verify Yim 2017 ENEURO.0348-16 directly** — agent's memory says k=2, θ≈100 µm; proposal #3 text says k=3, θ=50 µm | ~40 |
| Modular D1/D2 | `nx.stochastic_block_model(sizes=[250,250], directed=True)` | Burke 2017 Table 1: D1→D1 ~0.14, D1→D2 ~0.06, D2→D1 ~0.27, D2→D2 ~0.27; block-dependent log-normal weights with iSPN→dSPN 2× larger | ~30 |

Plus shared `assign_weights()` (~30 LOC) replacing broken `weight_generator.py`. Total refactor: **~200 LOC**.

### Critical gotchas
1. **NWS mean degree ≠ K.** Mean degree = K + p·(N-K-1). At N=500, K=8, P=0.01: actual mean degree ≈ 13. Compute and report; match to Snudda explicitly.
2. **NWS K=8 is 3-10× sparser than Snudda.** Real MSN connectivity at ~200 µm scale gives mean degree ~30-80. Either raise K to ~30, use configuration model, or **bracket NWS at multiple K** (cleanest scientifically).
3. **Cube size correction.** 300³ µm gives ~2300 MSNs at Oorschot density. **Use 180-200 µm cube** for ~500 MSNs.
4. **Burke probabilities are slice-distance (~50-100 µm)** intersomatic, not whole-cube. Naive application at larger distances over-counts; either restrict to short edges with distance falloff, or accept higher abs connectivity than measured.
5. **Reciprocity.** NWS undirected → directed must use **random orientation** (reciprocity ≈ 0, matches empirical low MSN reciprocity), NOT `to_directed()` (gives reciprocity = 1).
6. **Snudda multi-synapse aggregation.** (i,j) pairs can have several contacts in the HDF5; sum to a single weighted edge.
7. **MS-rewire weight handling.** `double_edge_swap` does NOT preserve weight-degree correlation. Use Rubinov-Sporns 2011 or Hanson 2024 for weighted nulls.

### Matching protocols (now 4, not 3)
- Match mean firing rate
- Match total excitatory drive
- Match input variance
- **NEW: match total inhibitory drive** — without this, topology effects may be confounded with mean-inhibition differences

### Weight distribution
**Use log-normal calibrated to Koos/Tepper/Wilson 2004** (mean ≈ 0.5 mV, CV ≈ 1). For Snudda graph specifically, use Snudda's native synaptic conductances from the HDF5. Cross-check by running level-2 weight matching across all five graphs.

---

## Analysis infrastructure

### Recommended package stack (in onboarding order)

| Order | Package | Version | Purpose |
|---|---|---|---|
| 1 | `neo` | 0.13+ | Canonical spike-train data model — **adopt first**, every later tool consumes it natively |
| 2 | `numpy`, `scipy`, `scikit-learn` | latest | Foundation; ridge, PCA, find_peaks, RidgeCV |
| 3 | `elephant` | 1.1+ | Spike-train stats, SPADE assembly detection, surrogates |
| 4 | `reservoirpy` | 0.3.12+ | Proposal #1 baseline; offline ridge readouts; NARMA generators |
| 5 | `powerlaw` | 1.5+ | Power-law fitting (Alstott/Bullmore/Plenz 2014); Vuong comparison |
| 6 | `ewstools` | 2.1+ | Early-warning signals (Bury 2021, 2023); variance, AC(1), spectral, deep-learning baselines |
| 7 | `mrestimator` | 0.1+ | Branching ratio (Wilting & Priesemann 2018) — bypasses avalanche-binning confound |
| 8 | `pyspike` | 0.8+ | ISI/SPIKE-distance, SPIKE-synchronization |
| 9 | `statsmodels` + `pymer4` | latest | Mixed-effects models for multiple-realization comparisons |
| 10 | `mne.stats` | 1.6+ | Permutation cluster tests for time-resolved comparisons |
| 11 | `diptest`, `cliffs_delta`, `kneed` | latest | Targeted utilities |
| 12 | `datalad` + Zenodo + CITATION.cff | — | Reproducibility infrastructure |
| 13 | `criticality` (Marshall lab Python port) | github HEAD | Shape collapses, DCC |

**Total onboarding budget: ~2.5 weeks of focused work** before benchmark experiments begin.

### Critical methodological warnings

1. **Dambre IPC has no production package.** Budget 1 full week, validate against Kubota's MATLAB output before trusting on STR. Reference implementations: github.com/kubota0130/ipc.
2. **NMF rank selection: don't use elbow.** Use bicross-validation (Owen & Perry 2009) or stability NMF (Wu et al. 2016), or Onken et al. 2016 protocol specifically for spike-train assemblies.
3. **Pairwise correlation under common Poisson input** must use **jitter-corrected correlation** (Smith & Kohn 2008): correlation on original minus jittered (σ=25 ms) spike trains, cancels stimulus-locked component.
4. **Avalanche-only criticality claims will be challenged in review** after Wilting/Priesemann 2018. Always report branching ratio (mrestimator) and shape collapse alongside power-law exponents.
5. **Power-law claims require BOTH** not rejecting power-law AND rejecting alternatives (log-normal, exponential, truncated power-law). Always report `powerlaw.distribution_compare` matrix.
6. **Multiple-comparison correction:** Benjamini-Yekutieli FDR (not BH) for dependent detectors. Use `statsmodels.stats.multitest.multipletests(method='fdr_by')`.
7. **Resample to uniform dt before any frequency-domain analysis.** Adaptive-dt time grid is incompatible with FFT/autocorr/Hilbert/avalanche-binning.
8. **Mixed-effects models required for multiple realizations.** Aarts et al. 2014 *Nat Neurosci* on pseudoreplication.
9. **Effect size + 95% bootstrap CI alongside every p-value.** No bare-p reporting (Lakens 2022).
10. **Pre-register on OSF before benchmark runs** for proposals #1 and #2 (#3 is exploratory by nature — pre-register hypotheses, allow parameter sweeps to be exploratory). ~4 hours; highest-leverage methodological move available.

### Ridge λ selection (proposal #1)
- `RidgeCV(alphas=np.logspace(-10, 4, 30), cv=None)` uses efficient LOO via SVD.
- **Scan λ over 14 orders of magnitude** — edge-of-chaos reservoirs legitimately need λ ≈ 1e-12, damped ones need λ ≈ 1.
- **Single held-out validation** is acceptable only if T_test ≥ 2τ_max. Lukoševičius 2012 specifically warns against k-fold for stationary tasks.

### Training length (proposal #1)
- "T_train > 10·N" is too coarse. Right answer: T_train >> N_eff / (1-ρ̄). For N=500 at edge-of-chaos: expect 10⁴-10⁵ steps after warmup.
- Always plot NRMSE-vs-T_train; report the elbow.

### Echo-state property (proposal #1)
- Two-trajectory test: initialize from two distinct states, drive with same input, monitor `||x_1(t) − x_2(t)||`. Steps to drop below 1e-6 = minimum warmup. Discard 2× as safety margin.
- Yildiz/Jaeger/Kiebel 2012 formalize this; spectral-radius helpers are NOT a substitute for spiking systems.

### Avalanche analysis (proposal #3)
Three principled approaches, recommend reporting all three:
1. **Multiple bin sizes** — report exponents across log-spaced bins 0.5×IEI to 4×IEI; the slope τ must be invariant over a half-decade.
2. **Branching ratio** via `mrestimator` (Wilting & Priesemann 2018) — bypasses subsampling-bias problem of avalanche counting.
3. **Time-rescaled exponents** (Lombardi et al. 2017).

---

## Validation gate before any production sweep

The current code must pass these tests before any sweep starts. Build the test suite alongside the refactor; don't defer it.

1. **Numerical regression.** Save a 1000-step trace at N=2 from current code (after bug fix #5 — `print` removal — so timing is honest). Every new implementation must reproduce it to <1e-6 relative error at matched dt.
2. **Quiescent stability.** I=0, I_ext=0, zero synaptic weights, 10 s. V relaxes monotonically to V_L; conductances decay analytically.
3. **Single-neuron convergence under Δt → 0.** Square current step, integrate at Δt ∈ {200, 100, 50, 25, 12.5, 6.25} µs. Fit `|V_h - V_ref|_∞ ∝ Δt^p`; require p ≈ 2 for Heun, p ≈ 1 for explicit Euler. V_ref from `solve_ivp(method='Radau', rtol=1e-12, atol=1e-14)`.
4. **Two-neuron delay timing.** Neuron A spikes at t=10 ms; neuron B onset within Δt of expected t=10+τ_D. **Will fail under current adaptive-dt + snap-up delay** — must pass after fix.
5. **Parameter sweep stability.** Sweep g_E_init, g_A_max, w_A, P each across 2 orders of magnitude. Tabulate any explosion (V > 100 mV or < -200 mV).
6. **Energy/charge conservation.** Total ∫I_membrane dt over passive relaxation = C·(V_init - V_L) to relative error 1e-4.
7. **Echo-state property** (proposal #1 specific).
8. **dt-stationarity** (proposal #2 specific): in quiescent network, dt should converge. Run 100 s; expect constant. Drift or oscillation = controller bug.
9. **Cross-integrator agreement.** Heun fixed-dt vs LSODA reference vs current adaptive Euler. Heun and LSODA must agree to ~1 mV on the slow envelope.

---

## Action plan — honest sequencing

### Week 0 — pre-flight fixes (1-2 days)

Bug fixes that block running on a modern Python stack. Do these even if you change nothing else.

1. Port NetworkX 1.x → 2.x/3.x throughout (`G.node` → `G.nodes`). 30-min mechanical change.
2. Fix non-int seed in `graph_build.py:8`.
3. Remove the 4 `print` calls in `math_functions.py:49-52`. **Immediate 10× speedup.**
4. Refactor `const.dt_list` out of module globals into a `Simulation` object or per-call return value.
5. Pin numerical reference: save N=2, T=1000 trace; write a pytest regression test.

### Week 1 — STR biophysics + numerical refactor (5 working days)

6. **Biophysics fixes:** `_a_A = 20`, `w_A = 0.5`, replace `g_K_max` at `update_functions.py:91` with new `g_I_max = 1.5e-9`, verify σ slope (likely needs unit correction), honor init conductances in `graph_build.py`. Document in code comments with citations.
7. **Commit STR spike-reset policy** to writing. Implement option B (threshold-reset) if pursuing proposal #3.
8. **Fix `weight_generator.py`** to produce log-normal weights (or whatever distribution is documented in the paper).
9. **State vectorization:** replace NetworkX node-attribute storage with NumPy arrays.
10. **Sparse adjacency + SpMV** for recurrent input.
11. **Ring buffer for delays** with integer-step indexing under fixed dt.
12. **Two integrator modes** (`fixed_dt_mode` Boolean): fixed-dt Heun + exp-Euler for #1/#3; existing adaptive Euler for #2.
13. **Switch to Poisson cortical drive** in place of constant `I`.

### Week 2 — graph infrastructure + analysis setup (5 working days)

14. Refactor `graph_build.py` to dispatch on `graph_type ∈ {nws, snudda, ms_rewire, gamma_kernel, modular}`. ~200 LOC.
15. Snudda install in Docker (FrontNeuralCircuits2021 tagged release); MSN-MSN HDF5 extraction script.
16. **Verify Yim 2017 Gamma parameters** directly from ENEURO.0348-16 (proposal text may be wrong; agent recall says k=2, θ≈100 µm).
17. Adopt `neo.SpikeTrain` as canonical spike data type.
18. Install analysis stack: `reservoirpy`, `elephant`, `ewstools`, `powerlaw`, `mrestimator`, `pyspike`, `pymer4`, `mne.stats`, `cliffs_delta`, `diptest`.
19. Pre-register proposals #1 and #2 on OSF (~4 hours).
20. Build validation-test suite (9 tests above).

### Week 3 — first pilot

Only after the validation gate passes. The original 2-week pilots from `RESEARCH_DIRECTIONS.md` can now begin honestly.

---

## Code-pointer summary

| File | Lines | Required changes |
|---|---|---|
| `const.py:8-10` | `_a_A = 1e3` → `20`; document τ_AHP = 50 ms | bug #1 |
| `const.py:25,28` | `_k`, `_beta` slope — verify units | bug #12 |
| `const.py:29` | `w_A = 0.01` → `0.5` | bug #2 |
| `const.py:30` | constant `I` → Poisson driver | bug #11 |
| `const.py:39` | `dt_list` out of module globals | bug #9 |
| `const.py:43-45` | `N=500, K=8, P=0.01` production defaults | needed for any real run |
| `const.py` (new) | `g_I_max = 1.5e-9` | bug #3 |
| `const.py` (new) | `fixed_dt_mode`, `dt_floor` | decision 2 |
| `graph_build.py:8` | `int(...)` seed | bug #6 |
| `graph_build.py:20-22` | honor init conductances | bug #8 |
| `graph_build.py` (full) | refactor to `graph_build(graph_type=..., **kwargs)` | graph battery |
| `weight_generator.py:13` | log-normal weights (real implementation) | bug #4 |
| `math_functions.py:39-53` | snap-up bias in `delay()` | bug #14; linear interp under adaptive |
| `math_functions.py:49-52` | remove `print` calls | bug #5 |
| `update_functions.py` (all) | NetworkX 2.x API; state vectorization; sparse SpMV; ring buffer; Heun+expEuler under fixed-dt | bugs #7, #10; decision 2 |
| `update_functions.py:39-40` | implement option B threshold-reset | decision 1 |
| `update_functions.py:91` | replace `g_K_max` with `g_I_max` | bug #3 |
| `update_functions.py:102` | per-neuron `f` logging | proposal #2 |
| `run.py` | per-step voltage logging for #1; HDF5 dump of dt_list and per-neuron f for #2 | infrastructure |
| `metrics/` (new directory) | reservoir readout, EWS detectors, NMF assembly pipeline | three pipelines |

---

## Per-proposal framework choice (now refined)

| Proposal | Stack | Compute strategy |
|---|---|---|
| #1 AHP reservoir | NumPy + scipy.sparse + reservoirpy + joblib | 7700 sims at N=500 → ~1 day on 16 CPU; ~2-6 hr on RTX 4090 with JAX vmap |
| #2 dt-as-instrument | NumPy + scipy.sparse + adaptive dt + h5py + scipy.integrate.solve_ivp(RK45) for cross-check | 1500 small sims → trivial on a workstation |
| #3 connectome atlas | Brian2 `cpp_standalone` + Snakemake | 6000 sims at N=500 → cluster or 1 week on 16 CPU; Brian2CUDA if N≥10k |

**One-framework-for-all option:** JAX. Autodiff for #1's Lyapunov work, `vmap` for sweeps, `lax.scan` for fixed-dt integration, easy CPU/GPU swap. Cost: 4-8 days learning curve, functional state plumbing.

---

## Citation list — implementation references

### Striatal biophysics
- Wilson, C.J. & Kawaguchi, Y. (1996). *J Neurosci* 16:2397.
- Mahon, Deniau, Charpier (2001 *J Neurosci* 21:5331; 2003 *J Neurosci* 23:4760).
- Nisenbaum, E.S. & Wilson, C.J. (1995). *J Neurosci* 15:4449.
- Wolf, Moyer, Lazarewicz et al. (2005). *J Neurosci* 25:9080.
- Steephen, J.E. & Manchanda, R. (2009). *J Comput Neurosci* 27:453.
- Humphries, Lepora, Wood, Gurney (2009). *Front Comput Neurosci* 3:26.
- Ponzi, A. & Wickens, J. (2010 *J Neurosci* 30:5894; 2013 *PLOS Comput Biol* 9:e1002954).
- Hjorth et al. (2020). *PNAS* 117:9554.
- Yim, Aertsen, Kumar (2017). *eNeuro* 4:ENEURO.0348-16.
- Bahuguna, Aertsen, Kumar (2015). *PLOS Comput Biol* 11:e1004233.
- Tepper, Wilson, Koos (2008). *Brain Res Rev* 58:272.
- Koos, Tepper, Wilson (2004). *J Neurosci* 24:7916.
- Burke, Rotstein, Alvarez (2017). *Neuron* 96:267.
- Pyle, R. & Rosenbaum, R. (2019). *Neural Computation* 31:1430.
- Toledo-Suárez, Duarte, Morrison (2014). *Front Comput Neurosci* 8:130.
- Oorschot, D.E. (1996). *J Comp Neurol* 366:580 (MSN density).

### Integration / delays
- Hines, M.L. (1984). *Int J Biomed Comput* 15:69.
- Mascagni, M. (1989). Numerical methods for neuronal modeling.
- Hines, M.L. & Carnevale, N.T. (1997). *Neural Comput* 9:1179 (NEURON).
- Brette et al. (2007). *J Comput Neurosci* 23:349.
- Stewart, R.D. & Bair, W. (2009). *J Comput Neurosci* 27:115 (Parker-Sochacki).
- Stimberg, M., Brette, R., Goodman, D.F.M. (2019). *eLife* 8:e47314 (Brian2).
- Morrison, A. et al. (2005). *Neural Comput* 17:1776 (NEST delay handling).
- Plesser, H.E. et al. (2007) (NEST parallel).
- Hanuschkin, A. et al. (2010). *Front Neuroinform* 4:113 (off-grid spikes).
- Söderlind, G. (2002). *Numerical Algorithms* 31:281.
- Söderlind, G., Jay, L., Calvo, M. (2015). *BIT Numer Math* 55:531.
- Calvo, M., Higham, D.J., Montijano, J.I., Rández, L. (1997). *IMA J Numer Anal* 17:521.
- Hairer, E., Nørsett, S.P., Wanner, G. (1993). *Solving ODEs I*.
- Hairer, E., Wanner, G. (1996). *Solving ODEs II*.
- Bellen, A., Zennaro, M. (2003). *Numerical Methods for DDEs*.
- Engelken, R., Wolf, F., Abbott, L.F. (2023). *Phys Rev Research* 5:043044.

### Performance / Python
- Stimberg/Brette/Goodman 2019 (Brian2).
- Brian2CUDA: brian2cuda.readthedocs.io.
- Bradbury, J. et al. (JAX) — docs.jax.dev.
- Trouvain, N. et al. (reservoirpy) — reservoirpy.readthedocs.io.
- joblib.readthedocs.io; snakemake.readthedocs.io.

### Graphs / null models
- Watts, D.J. & Strogatz, S.H. (1998). *Nature* 393:440.
- Newman, M.E.J. & Watts, D.J. (1999). *Phys Lett A* 263:341.
- Maslov, S. & Sneppen, K. (2002). *Science* 296:910.
- Milo, R. et al. (2003). arXiv:cond-mat/0312028.
- Rubinov, M. & Sporns, O. (2010 *NeuroImage* 52:1059; 2011 *NeuroImage* 56:2068).
- Vasa, F. & Misic, B. (2022). *Nat Rev Neurosci* 23:493.
- Hanson, J.O. et al. (2024). *Nat Comput Sci*.
- Hellwig, B. (2000). *Biol Cybern* 82:111 (distance-dependent kernels).

### Analysis / statistics
- Dambre, J., Verstraeten, D., Schrauwen, B., Massar, S. (2012). *Sci Rep* 2:514 (IPC).
- Legenstein, R. & Maass, W. (2007). *Neural Networks* 20:323.
- Lukoševičius, M. (2012). *Neural Networks: Tricks of the Trade* (ESN practical guide).
- Bernacchia, A. et al. (2011). *Nat Neurosci* 14:366.
- Yildiz, I.B., Jaeger, H., Kiebel, S.J. (2012). *Neural Networks* 35.
- Gao, P. & Ganguli, S. (2015). *Curr Opin Neurobiol* 32.
- Bury, T.M. et al. (2021 *J R Soc Interface*; 2023 *Nat Commun* 14:7436) — ewstools.
- Alstott, J., Bullmore, E., Plenz, D. (2014). *PLOS ONE* 9:e85777 (powerlaw).
- Clauset, A., Shalizi, C.R., Newman, M.E.J. (2009). *SIAM Rev* 51.
- Klaus, A., Yu, S., Plenz, D. (2011). *PLOS ONE* 6:e19779.
- Wilting, J. & Priesemann, V. (2018). *Nat Commun* 9:2325 (mrestimator).
- Marshall, N. et al. (2016). *Front Physiol* (NCC toolbox).
- Petermann, T. et al. (2009). *PNAS* 106:15921.
- Beggs, J.M. & Plenz, D. (2003). *J Neurosci* 23:11167.
- Renart, A. et al. (2010). *Science* 327.
- Tetzlaff, T., Helias, M., Einevoll, G.T., Diesmann, M. (2012). *PLOS Comput Biol* 8:e1002596.
- Smith, M.A. & Kohn, A. (2008). *J Neurosci* 28 (jitter-corrected correlation).
- Mulansky, M. & Kreuz, T. (2016). *SoftwareX* 5:183 (pyspike).
- Denker, M., Yegenoglu, A., Grün, S. (2018). *Front Neuroinform* (elephant).
- Quaglio, P. et al. (2017). *Front Comput Neurosci* 11 (SPADE).
- Onken, A. et al. (2016). *PLOS Comput Biol* 12:e1005189 (NMF rank for spike assemblies).
- Owen, A.B. & Perry, P.O. (2009). *Ann Appl Stat* 3 (bicross-validation).
- Wu, S., Joseph, A., Drton, M., Witten, D. (2016). *PNAS* 113 (stability NMF).
- Aarts, E. et al. (2014). *Nat Neurosci* 17:491 (pseudoreplication).
- Maris, E. & Oostenveld, R. (2007). *J Neurosci Methods* 164:177 (permutation cluster).
- Benjamini, Y. & Yekutieli, D. (2001). *Ann Stat* 29 (BY FDR).
- Lakens, D. (2022). *Annu Rev Psychol* 73 (effect-size reporting standards).
- van de Schoot, R. et al. (2021). *Nat Rev Methods Primers* 1:1 (Bayesian).
- Pikovsky, A. & Rosenblum, M. (2015). *Chaos* 25 (Kuramoto).
