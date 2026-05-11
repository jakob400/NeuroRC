# NeuroRC — Publishable Research Directions

A compiled report of three deep-dive literature reviews into specific publishable extensions of this codebase. Each candidate has been (a) checked for the most damaging "already done" paper that could kill it at peer review, (b) fleshed out into a concrete experimental plan, and (c) given a 2-4 week pilot with a pre-committed falsification criterion.

The three candidates emerged from two prior rounds covering ten angles (reservoir computing, criticality, dopamine, plasticity, topology, information theory, adaptive-dt-as-instrument, TDA, controllability, connectome reality check). Most obvious framings are saturated; the three below survived blind-spot hunting.

---

## Executive summary

| # | Title | Novelty | Feasibility | Publishability | Kill paper? | Top risk |
|---|---|---|---|---|---|---|
| 1 | **AHP conductances as a network-level timescale reservoir** (STR vs LIF on matched small-world graphs) | High | High | High (Neural Comp ~40-50%) | None | LIF-leak-heterogeneity control might match STR on MC |
| 2 | **dt(t) as a real-time dynamical observable** for E/I-balance and synchronization onsets | Very high | Medium-High (pilot needed) | Medium-High (Chaos / Front Neuroinform) | None | "This is folklore" objection at review |
| 3 | **Necessary structural features for striatal dynamics** — null-model atlas (NWS / Snudda / degree-preserving / distance-dependent / modular) | High | Medium (Snudda install) | High (Network Neuroscience ~50%) | None confirmed, but Kotaleski-lab scoop risk ~30% in 6 months | Snudda group releases their own dynamics extension |

The three proposals make **incompatible demands on the integrator** — see "Shared infrastructure and the integrator fork" below. They are genuinely separate studies that share most of the codebase.

---

## Saturated territory — what NOT to chase

The two prior rounds identified the following framings as closed or near-closed by existing work:

- Small-world × spiking × avalanches / criticality (closed by Borges 2021, Massobrio 2015, Girardi-Schappo 2022)
- "Striatum as reservoir" conceptual framing (closed by Dominey lineage 1995-2018, Ponzi/Wickens 2010-2016, Pyle/Rosenbaum 2019)
- STDP × small-world × synchronization (closed by Wang/Perc 2014, Kim/Lim 2018, Pena 2019)
- D1/D2 dopamine-modulated microcircuit (owned by Bahuguna/Kumar, Humphries, Hjorth/Kotaleski)
- "Striatal criticality" (Petermann/Plenz 2016: striatum is explicitly non-critical)
- Generic (N, K, P) sweep papers (will be desk-rejected in 2026)
- Pure persistent-homology of spike rasters without LIF↔STR substrate comparison (closed by Bardin/Spreemann/Hess 2019)

---

## The convergent insight

Across all 10 literature-review angles, the same finding kept resurfacing: **the codebase's only genuinely unique asset is having STR (conductance-based, with AHP + voltage-gated K) and LIF on identical graphs with identical inputs.** Seven of ten angles independently landed on this as the publishable hook. Two of the three proposals below (#1, #3) lean directly on it. The third (#2) is independent — it exploits the integrator design.

---

# Proposal 1 — AHP conductances as a tunable network-level timescale reservoir

## One-sentence claim

In a fixed small-world reservoir, biophysical AHP and voltage-gated potassium conductances jointly produce a broader per-neuron autocorrelation-timescale distribution and higher Jaeger memory capacity than any rate-matched LIF reservoir — including LIF with a tuned per-neuron leak distribution — establishing biophysical adaptation as the network-level mechanism for the timescale reservoir originally described in single neurons by Bernacchia et al. (2011).

## Literature landscape

The relevant literature has three concentric circles:

**Single-cell timescale reservoir (the anchor):** Bernacchia, Seo, Lee, Wang (2011, *Nature Neuroscience*) measured a distribution of integration time constants across PFC/ACC/parietal neurons in monkeys performing reward-history tasks. The "reservoir of time constants" framing is theirs. They never extended it to networks.

**Adaptation in spiking networks (the threats):**
- Salaj, Subramoney, Bellec, Legenstein, Maass (2021, *eLife*) — spike-frequency adaptation (SFA) via adaptive threshold (GLIF2) in trained spiking networks; matches LSTM-level on temporally dispersed tasks.
- Bellec, Salaj, Subramoney, Legenstein, Maass (2018, *NeurIPS*; arXiv:1803.09574) — LSNN, adapting-threshold LIF.
- Perez-Nieves, Goodman et al. (2021, *Nature Communications*) — heterogeneous τ_m/τ_s in LIF improves temporal-task performance.
- Saray/Engelken/Wolf et al. (2025, *Nature Communications*) — "Boosting reservoir computing with brain-inspired adaptive E/I balance"; orthogonal mechanism.

**Closest priority claim:** Toledo-Suárez, Duarte, Morrison (2014, *Front Comput Neurosci*) — striatal microcircuit reservoir using a multi-timescale adaptive threshold (MAT). Mackey-Glass + trajectory generation. **No Jaeger MC sweep, no conductance-based model, no LIF baseline, no adaptation-strength sweep.** This is a prior-art citation, not a competitor.

**The wedge:** Shi, Engelken, Sompolinsky, Wolf (2023, *eLife*, "A reservoir of timescales emerges in recurrent circuits with heterogeneous neural assemblies") explicitly tested whether heterogeneous single-cell τ generates a heterogeneous network-level timescale spectrum and found it does **not** — the spectrum emerges from cluster-size self-coupling, not from per-neuron τ-heterogeneity. This *predicts* the LIF-het control will fail to match STR, which is exactly the result this paper needs.

## The closest papers to engage

| Citation | Severity | Distinguishing claim available to us |
|---|---|---|
| Salaj et al. 2021 *eLife* | Moderate | Their networks are trained end-to-end with BPTT/e-prop, not fixed reservoirs; no Jaeger MC; SFA implemented as adaptive threshold, not conductance with reversal potential |
| Perez-Nieves & Goodman 2021 *Nat Commun* | Moderate | Trained SNN, not reservoir; τ-heterogeneity only, no adaptation channel; no biophysical reversal potentials. Properly framed as the LIF-het *baseline* our work must beat |
| Toledo-Suárez et al. 2014 *Front Comp Neuro* | Mild (prior art) | Striatal MAT reservoir but no MC sweep, no conductance model, no LIF baseline |
| Shi et al. 2023 *eLife* | Mild (*supports* our hypothesis) | Their network-level result predicts our LIF-het control will fail — citable as motivation |
| Grzyb et al. 2009 (HH LSM) | Very mild | Pattern recognition only; no MC, no IPC, no LIF baseline |
| Bernacchia et al. 2011 *Nat Neuro* | Anchor | Single-cell scope; our title generalizes their claim to a biophysical network |

## Verdict: no kill paper. The gap is real and narrow.

The specific combination — fixed reservoir + biophysical conductance adaptation (AHP + voltage-gated K with proper reversal potentials) + Jaeger MC + IPC decomposition + LIF-leak-heterogeneity control — has not been published.

## Experimental plan

### Tasks (four, dropping anything broader)
1. Jaeger linear memory capacity MC = Σₖ corr²(u(t-k), y_k(t)) over k = 1..K_max
2. NARMA-10 NRMSE
3. Lorenz one-step-ahead (sanity benchmark only)
4. Delayed pattern XOR (probes adaptation-trace memory directly)

Drop SHD, audio benchmarks, Mackey-Glass.

### Readout
Ridge regression on exponentially-filtered voltage state x_i(t) = (voltage_i ∗ exp(-t/τ_ro))(t) with τ_ro = 20 ms (fixed; not swept — otherwise confounds reservoir memory with readout memory). λ chosen by leave-one-out CV per task per network.

For LIF, additionally report a sister condition with exponentially-filtered spike trains.

### The critical LIF-leak control (paper lives or dies here)

Implement three LIF variants:
- **LIF-homo:** single global τ_m, swept on log grid {1, 3, 10, 30, 100} ms
- **LIF-het:** τ_m per-neuron from log-uniform [τ_min, τ_max]; sweep range τ_max/τ_min ∈ {1, 3, 10, 30, 100}. This is the Perez-Nieves/Goodman setup.
- **LIF-ALIF:** LIF + adaptive threshold (Bellec/Salaj/Maass style)

The headline claim must be: STR achieves a memory-capacity / timescale profile that **none of LIF-homo, LIF-het, LIF-ALIF reproduces at matched firing rate and topology**. If LIF-het matches STR, there is no paper.

### Sweep design
- Adaptation: α ∈ {0, 0.25, 0.5, 1, 2, 4} × g_A_max; β ∈ {0, 0.5, 1, 2} × g_K_max. 6×4 grid.
- Network: fix N=500, K=8, P=0.01 for main result; sweep K ∈ {4, 8, 16} and P ∈ {1e-4, 1e-2, 5e-2, 0.2} as topology robustness check at default adaptation only.
- Firing-rate matching: tune drive so STR and LIF population mean rate match r* ∈ {2, 10, 20} Hz within ±10%. Also match CV_ISI within 20%. Report both matched and unmatched.
- Realizations: 20 graph seeds × 3 input seeds.

### Metrics
- Linear MC, with K_max = 2× slowest intrinsic timescale.
- Information processing capacity (IPC) decomposition by polynomial degree (Dambre et al. 2012).
- Kernel rank and generalization rank (Legenstein & Maass 2007).
- Participation ratio of voltage covariance (effective dimensionality).
- Per-neuron autocorrelation decay τᵢ distribution — the direct empirical signature of the "timescale bank."

### Statistics
Primary confirmatory test: STR(α=1, β=1) vs best-tuned LIF-het across MC, NARMA, XOR. Permutation test (10,000 shuffles) on network-level mean, Holm-Bonferroni across four tasks. Cliff's δ effect size.

## 2-4 week pilot

- **Week 1:** Fix N=500 in `const.py`. Add per-neuron g_L distribution to LIF. Add ALIF variant. Add ridge readout with LOO-CV λ selection.
- **Week 2:** Build firing-rate calibration. For one network seed, find I_ext (LIF) and I (STR) giving 10 Hz at α=1, β=1. Verify stability.
- **Week 3:** Run MC and NARMA-10 on STR-default, LIF-homo-tuned, LIF-het, LIF-ALIF-tuned. 5 seeds each.
- **Week 4:** Diagnostic. **Falsification criterion:** if STR > LIF-het by ≥20% on MC AND per-neuron τᵢ distribution from STR is visibly broader than from LIF-het, proceed. Otherwise pivot to a τᵢ-shape-only claim or abandon.

## 3-6 month plan

- **Month 1:** Pilot + reservoir echo-state-property validation.
- **Month 2:** Full adaptation grid (α × β), 10 seeds, single topology.
- **Month 3:** Topology sweep at headline points; IPC decomposition; Lorenz sanity.
- **Month 4:** Statistical writeup; begin draft.
- **Month 5:** Robustness — alternative readout, alternative rate targets, N=200/1000 replications.
- **Month 6:** Manuscript and submission.

## Target venue

| Venue | Acceptance odds | Rationale |
|---|---|---|
| Neural Computation | 40-50% | Best fit; accepts careful biophysical reservoir analysis |
| Frontiers Comp Neuro | 60-70% | High acceptance; Toledo-Suárez precedent |
| PLOS Comp Bio | ~25% | Needs stronger biological framing |
| Cosyne abstract | ~80% | Parallel submission for visibility |

## Risk register

1. **LIF-het matches STR** (likely failure mode, given Perez-Nieves 2021). Pilot designed to detect; pivot to τᵢ-shape claim.
2. **STR is not really spiking** — no reset in current code. Decide week 1: subthreshold-continuous (citable to Pyle & Rosenbaum 2019) or add reset.
3. **Rate-matching fails.** Report multiple rate targets; if STR cannot match LIF without exotic parameters, frame as a finding.
4. **Adaptive global dt confounds the comparison.** STR and LIF run on different time grids. **Must convert to fixed dt (e.g., 0.1 ms RK4) before any cross-model comparison.** Non-negotiable.
5. **Scoop in 6 months.** Goodman lab and Salaj/Maass group are active. Mitigation: pre-register, post bioRxiv at month 4 draft stage.

## Go/no-go

**Go, conditional on pilot.** No kill paper exists. The 2-4 week pilot is the proper gate.

---

# Proposal 2 — dt(t) as a real-time dynamical observable

## One-sentence claim

The variable timestep stream that every adaptive ODE solver already emits is a free, network-level finite-time-Lyapunov proxy, and on coupled spiking neurons it detects E/I-balance breakdown and synchronization onset earlier and with higher SNR than the standard early-warning toolbox (variance, lag-1 autocorrelation, spectral entropy) — at no extra compute cost.

## Theoretical groundwork

The codebase computes dt(t) = ε / maxⱼ |fⱼ(t)| where fⱼ runs over every state-variable RHS of every node. Taking logs:

```
log(1/dt(t)) = log maxⱼ|fⱼ(t)| − log ε
```

The quantity log maxⱼ|fⱼ| is closely related to the logarithmic norm μ(J(t)) of the system Jacobian along the trajectory. Söderlind/Jay/Calvo (2015) formalize this as a "stiffness indicator" defining a local reference timescale. Our dt is a cheap proxy that uses |f| instead of |μ(J)| — exact when f is locally linear in the direction of fastest motion. So:

```
log(1/dt(t)) ≈ λ_local(t) + const   when ẋ ≈ J(t)x
```

The finite-time Lyapunov-like average is then Λ(T) = (1/T) ∫₀ᵀ log(1/dt) dt', which the codebase already computes for free in `const.dt_list`.

**Crucial distinction from prior art:** existing literature (Calvo/Higham 1997, Söderlind/Jay/Calvo 2015, Scheffel 2024) uses a local-LE concept *inside the controller* to choose dt. Our proposal reverses this — *read out the controller's chosen dt as a network-level observable.*

## Literature landscape

**Numerical analysis (the closest hits):**
- Söderlind, Jay, Calvo (2015, *BIT Numerical Mathematics* 55:531-558, "Stiffness 1952-2012: Sixty years in search of a definition"). Defines a stiffness indicator from logarithmic norms; explicitly notes it distinguishes "locally unstable turning points" in van der Pol and Oregonator. The closest published statement that step-size-like quantities are diagnostics of dynamics, not just controller parameters. Confined to single-system ODEs.
- Scheffel (2024, arXiv:2402.17030, "Transforming Stiffness and Chaos"). Defines Q(t) ≡ dt_max/dt_stiff as "a more intuitive measure of stiffness... continually evaluated for determining local stiffness or chaoticity." Applies only to Lorenz, Robertson, van der Pol. No networks, no neural systems, no EWS comparisons. **This is the closest published cousin to our proposal — same scalar functional, different application.**
- Calvo, Higham, Montijano, Rández (1997, *IMA J. Numer. Anal.*) — stepsize from Lyapunov theory.
- Söderlind (2002, *Numerical Algorithms* 31:281-310) — automatic control of adaptive timestepping (digital-filter framing).

**Computational fluid dynamics & N-body:**
- Pham, Rein, Spiegel (2024, arXiv:2401.02849) — new timestep criterion for N-body. Adjacent only.
- ShockCast (2025, arXiv:2506.07969) — ML-predicted CFL-style timestep. Treats dt as a prediction target.

**Computational neuroscience adjacent:**
- Engelken, Wolf, Abbott (2023, *Phys Rev Research*) — Lyapunov spectra of chaotic RNNs. Full-spectrum, expensive, no dt-proxy. **Complements our work**: their gold-standard measurement validates our cheap free read-out.
- Engelken (2024, arXiv:2412.21188) — "sparse chaos in cortical circuits"; the largest LE itself is bursty at network level.
- Hines/Carnevale NEURON CVODE wrapper: exposes dt, but nothing in NEURON documentation proposes analyzing the dt sequence.

**Early-warning signals literature:**
- Scheffer et al. (2009, *Nature*) — canonical EWS review.
- Maturana et al. (2020, *Nat Commun*) — critical slowing down as seizure biomarker.
- Wilkat, Rings, Lehnertz (2019, *Chaos*) — "no evidence for critical slowing down prior to human epileptic seizures." This is an opportunity: motivates "the standard EWS pipeline fails — can a numerics-derived signal succeed?" framing.
- Mormann et al. (2007, *Brain*) — canonical seizure-prediction review.
- Boettiger & Hastings (2012, *J R Soc Interface*) — prosecutor's fallacy.

## The closest papers to engage

| Citation | Severity | Distinguishing claim available to us |
|---|---|---|
| Scheffel 2024 arXiv:2402.17030 | Moderate (same scalar functional) | Single-system ODEs only (Lorenz, van der Pol); solver-side telemetry framing, not biological observable; no EWS benchmark |
| Söderlind/Jay/Calvo 2015 BIT | Moderate | Single ODEs; never read out as time-series; never benchmarked against EWS |
| Pham/Rein/Spiegel 2024 (N-body) | Mild | Different observable; doesn't propose dt as physical readout |
| ShockCast 2025 | Mild | dt as prediction target, not observable |
| Maturana 2020 / Wilkat 2019 (EWS in epilepsy) | Mild (opportunity) | Motivates the "EWS toolbox fails — try this instead" framing |
| Engelken/Wolf/Abbott 2023 | Mild (complementary) | Their full LE spectrum validates our cheap proxy |
| NEURON CVODE docs / Brian2 | Folkloric (no published statement) | The trick may be known but unwritten — published folklore is folklore |

## Verdict: no kill paper. Both Scheffel and Söderlind/Jay/Calvo must be cited prominently on page 1.

## Experimental plan

### Target transitions and oracles
1. **E/I balance breakdown.** Sweep global inhibitory scaling ρ. Oracle: variance of population rate r(t) crosses 5× pre-transition baseline within 50 ms window.
2. **Synchronization onset.** Sweep NWS (P, K). Oracle: Kuramoto order parameter R(t) from Hilbert-transformed Vm crosses 0.5.
3. **Up/down bistability.** Requires extending STR with slow K adaptation (~30 LOC, 2-3 days). Oracle: Hartigan dip test on Vm histogram, p < 0.01.
4. **Seizure-like cascade.** Ramp g_A_max from 25 nS to 5 nS. Oracle: avalanche-size distribution cutoff exceeds 10% of N within 10 ms window.

### Baseline detectors
All evaluated on the same downsampled r(t) (binned to 1 kHz):
- σ²_r(t): rolling variance, 200 ms window, 10 ms step
- AC(1): lag-1 autocorrelation
- H_spec(t): spectral entropy, Welch with 256-sample segments
- Benettin largest LE: Gram-Schmidt re-orthogonalization every 1 ms. **Borderline at N=500** — restrict to N=100 as reference oracle only.
- Our detector: S(t) = log(1/dt(t)), low-pass filtered at 100 Hz, z-scored on 1-s rolling window

### Detection metric
For each transition type, oracle yields true transition time t*. Detector d crosses fixed-false-positive-rate threshold at t_d. Lead time τ_d = t* − t_d. Primary metrics:
- ROC AUC for "transition within next 100 ms" sliding label
- Lead-time distribution (Wilcoxon signed-rank, 100 seeds)
- Lead-time at 5% FPR

### Controls — the most damaging confound
maxⱼ|fⱼ| could be dominated by a single neuron unrelated to the population transition:
- Per-neuron dtⱼ = ε/|fⱼ|; analyze distribution.
- Subsampled max: dt_S = ε/max_{j∈S}|fⱼ| over random 50-node subsets.
- 95th-percentile dt instead of max.
- AHP-conductance dependence: if signal collapses when AHP is off, the dt-signal is just an AHP-clock artifact.
- Regress S(t) on r(t); detector must beat AC(1) on residuals.

## 2-week pilot

Single transition (synchronization onset, NWS K-sweep), N=200, 50 seeds × 30 K-values. Compute S(t), σ²_r, AC(1) on same downsampled grid.

**Falsification criterion:** S(t) must beat *both* σ²_r and AC(1) in mean lead-time at 5% FPR by ≥20 ms (Wilcoxon p < 0.05).

If S fails this cheap test, abandon. ~3 days compute + ~3 days analysis. Code changes: ~150 LOC (CSV writer for dt_list, four-detector metrics module, Kuramoto oracle).

## 3-6 month plan

- **Month 1:** Pilot + STR refactor for per-neuron dtⱼ; add Hilbert-Vm Kuramoto; add E/I scaling sweep.
- **Month 2:** Add slow-K adaptation for up/down bistability; Hartigan dip oracle; AHP-ramp protocol.
- **Month 3:** Benettin LE at N=100 as gold standard; show ρ(Λ_Benettin, S(t)) > 0.7.
- **Month 4:** Full N=500, all four transitions, all baselines, all controls.
- **Month 5:** Robustness (NWS-P, ε-sensitivity); Brian2 reimplementation as portability check — if S survives the port, we have a tool, not a NeuroRC artifact.
- **Month 6:** Writing.

## Target venue

| Venue | Acceptance odds | Rationale |
|---|---|---|
| Chaos (AIP) | ~35% | Strong fit for dynamical-systems framing; reviewers will know Söderlind/Scheffel — must cite up front |
| Front Neuroinform (Methods) | ~50% | Fast review, simulator-side observable fits perfectly |
| J Comput Neurosci | ~30% | Receptive; reviewers will demand full LE comparison |
| Neural Computation | ~25% | Likes formalism; LE-proxy theorem must be airtight |
| PLOS Comp Bio | ~20% | Needs biological prediction beyond simulation |
| Phys Rev E | ~20% | Physics novelty thin without analytical scaling result |

**Recommendation:** Chaos first if LE-proxy formalism is tight; Front Neuroinform as fallback.

## Risk register

1. **"Folklore" objection at review.** "Everyone in NEURON/Brian knows dt drops near spikes." Defense: cite Scheffel/Söderlind explicitly; novel contribution is network observable + EWS benchmark, not the existence of the effect.
2. **dt dominated by single-neuron artifacts.** Pilot will detect; per-neuron and subsampled controls are the answer.
3. **Pilot fails: S does not beat AC(1)+variance** (~30% probability). Honest stop condition built in.
4. **Scoop from CFD/N-body during the 6-month window** (ShockCast 2025 shows the field is moving). Draft a short companion preprint after pilot success.
5. **Reviewer demands full Benettin LE at N=500.** Achievable but costly; budget 2 weeks compute.

## Go/no-go

**Go, conditional on pilot.** Söderlind/Jay/Calvo (2015) and Scheffel (2024) are real predecessors that must be cited as the closest mathematical kin, but both are confined to single-system ODEs and solver-side diagnostics. The contribution is novel.

---

# Proposal 3 — Necessary structural features for striatal dynamics: a null-model atlas

## One-sentence claim

By running identical biophysical dynamics on five carefully matched graph nulls — including a Snudda-derived MSN subgraph and its degree-preserving rewire — we produce the first feature-by-signature necessity matrix for striatal dynamics, transferring the Gal/Reimann/Markram 2020 cortical framework to the basal ganglia and answering the question Carannante 2024 explicitly left open.

## Literature landscape

**Cortical precedent (the template):**
- Gal, López-Cruz, Reimann, Markram et al. (2020, *Network Neuroscience*, DOI 10.1162/netn_a_00126) — "Impact of higher-order network structure on emergent cortical activity." Identical dynamics on the NMC reconstruction vs cloud-model control with matched first-order but reduced higher-order structure. The exact framing we extend.
- Reimann et al. (2017, *Front Comput Neurosci*) — "Cliques of Neurons Bound into Cavities"; the structural side.

**Snudda program (the threat surface):**
- Hjorth et al. (2020, *PNAS*) — "The microcircuits of striatum in silico." Full-scale ~10k mouse dorsal striatum (dSPN, iSPN, FSI, ChIN, LTS) with touch-detection connectivity. State of the art.
- Hjorth, Hellgren Kotaleski, Kozlov (2021, *Neuroinformatics*) — Snudda pipeline paper.
- Frost Nylén et al. (2023, *PNAS*) — surround inhibition.
- **Carannante, Scolamiero, Hjorth, Kozlov, Kumar, Chacholski, Hellgren Kotaleski (2024, *Network Neuroscience*)** — Snudda + topological data analysis (directed cliques) on PD-progression graphs. **Uses pruning, not degree-preserving rewires.** **Measures only directed-clique counts and input-output curves — not assembly switching, dwell-time distributions, ISI tails, or pairwise correlations.** Explicitly defers full activity dynamics to future work. This is the most threatening paper but it is also our most useful citation.
- Frost Nylén/Grillner et al. (2025, *PNAS*) — habit formation in basal ganglia. Plasticity, not topology.
- Thompson et al. (2025, *PNAS*) — SNr synaptic integration, not striatum.

**Snudda public repo audit (May 2026):** 47 branches inspected. `PD_topology` last commit Sep 2023 (= Carannante 2024). `input_output_analysis` last Nov 2022. `connectivity` last Apr 2022. Recent 2026 commits: spine biophysics, kaf_ms bugfix, morphology degeneration. **No active branch on null-model graph ablation.** Scoop probability from unpublished Snudda code: low.

**Adjacent striatal modeling:**
- Belić et al. (2024, *Front Comput Neurosci*, 18:1410335) — pathological cell assembly dynamics; uses Erdős-Rényi (p=0.4) lateral connectivity, no graph-type comparison.
- Yim, Aertsen, Kumar (2017, *eNeuro*) — distance-dependent Gamma kernel → AI/TA/WTA regimes. Single-graph-family.
- Spreizer, Aertsen, Kumar (2019, *PLOS Comp Biol*) — distance-dependent followup on generic spiking nets.
- Bahuguna, Aertsen, Kumar (2015, *PLOS Comp Biol*) — DA-modulable Go/No-Go threshold.
- Ponzi & Wickens (2010 *J Neurosci*; 2013 *PLOS Comp Biol*) — sparse asymmetric inhibitory → cell-assembly switching. The signature we measure.

**Null-model methodology:**
- Vasa & Misic (2022, *Nat Rev Neurosci*) — canonical null-models review.
- Betzel & Bassett (2017, *J Roy Soc Interface*) — generative models.
- Sizemore et al. (2018, *J Comput Neurosci*) — clean clinical example.
- Hanson et al. (2024, *Nat Comput Sci*) — weighted null algorithm.

**Striatal target signatures (well-characterised):**
- Ponzi & Wickens (2010-2013) — assembly switching, ISI tail.
- Klaus & Plenz (2016, *PLOS Biology*, 10.1371/journal.pbio.1002582) — low-correlation non-critical signature under cortical avalanche drive.
- Wilson & Kawaguchi (1996) — up/down states.
- Burke, Rotstein, Alvarez (2017, *Neuron*) — asymmetric iSPN→dSPN > dSPN→iSPN.

## The closest papers to engage

| Citation | Severity | Distinguishing claim |
|---|---|---|
| Carannante 2024 *Net Neurosci* | Moderate (closest hit) | Uses pruning not rewires; only clique counts not Ponzi/Wickens/Plenz signatures; explicitly defers full activity dynamics — we are that follow-up |
| Belić 2024 *Front Comp Neuro* | Moderate | Single graph (random p=0.4); their result is one cell in our atlas |
| Gal/Reimann/Markram 2020 *Net Neurosci* | Template (not competitor) | They did cortex; nobody has done striatum |
| Yim/Kumar 2017 *eNeuro* | Mild | Owns Gamma-kernel-shape story; we use as one battery node |
| Spreizer/Kumar 2019 *PLOS CB* | Mild | Generic spiking; not striatum-specific |
| eLife reviewed preprint 99402 | Mild | Mean-field tractability + RL; orthogonal |
| Snudda repo branches | Low scoop risk | No active null-model work in 2026 |

## Verdict: no kill paper. The framing is currently unoccupied. Move now.

## Experimental plan

### The five-graph battery (~500 nodes, MSN-only edges)

**(i) Newman-Watts-Strogatz** — codebase default; biologically unmotivated control.

**(ii) Snudda-derived MSN-MSN subgraph.** Generate 10k-neuron striatum from Snudda FrontNeuralCircuits2021 tagged release in Docker. Filter to MSN-MSN edges. Downsample to ~500 by taking a *contiguous spatial subvolume* (preserves distance-dependent signature). Preserve D1/D2 as node attribute. ~3-5 days engineering.

**(iii) Maslov-Sneppen degree-preserving rewire of (ii).** `networkx.double_edge_swap(G, nswap=10m)`. Verify mixing by clustering plateau. 30 realizations per (ii) realization.

**(iv) Distance-dependent (Yim/Aertsen/Kumar 2017 Gamma kernel).** 500 nodes in 300×300×300 µm cube. Gamma shape k≈3, scale θ≈50 µm (peak at ~100 µm, near-neighbor suppression). Prefactor tuned to match Snudda mean degree.

**(v) Block-modular D1/D2 with Burke 2017 asymmetry.** Block sizes 250 D1 + 250 D2. Burke Table 1 probabilities: D2→D2 ≈ 27%, D2→D1 ≈ 27%, D1→D1 ≈ 14%, D1→D2 ≈ 6%. Weights scaled by Burke IPSC amplitudes (D2 inputs ~2× D1).

20 realizations per graph type.

### Dynamical signatures

**(a) Ponzi-Wickens assembly switching.** 100 ms binned spikes over 30 s sim. PCA → NMF on binned matrix; argmax assembly index at each t; dwell-time distribution (KS test vs exponential); slow population covariance eigenvalue spectrum; ISI Pareto tail fit.

**(b) Petermann/Plenz low-correlation non-critical signature.** Pairwise correlation distribution (10 ms bins, 1000 random pairs). Avalanche size distribution under Plenz-style avalanche-modulated input drive. Clauset power-law fit.

**(c) Firing-rate distribution.** Log-binned histogram. KS distance to log-normal. Silent-fraction (<0.1 Hz).

### Cortical drive
Two regimes, run both:
- **Regime A:** Independent Poisson, 1 kHz aggregate per neuron, exponential conductance kicks.
- **Regime B (Petermann/Plenz):** Common Poisson modulated by Plenz-style avalanche envelope (size-frequency power-law α=1.5).

### Matching protocol — critical
Run each comparison three ways:
1. Match mean firing rate to 2 Hz.
2. Match total excitatory drive (drive × K constant).
3. Match input variance (Poisson rate × num inputs constant).

A signature is "robustly graph-dependent" only if it differs across all three matchings.

### Necessary-vs-sufficient inference

| Comparison | Isolates |
|---|---|
| Snudda vs Maslov-Sneppen rewire | non-degree topology (clustering, modules, motifs) |
| NWS vs MS-rewire | clustering + path-length specifically |
| Snudda vs distance-dependent at matched degree | spatial embedding being sufficient |
| Modular-D1/D2 vs MS-rewire | D1/D2 asymmetry specifically |
| LIF vs STR axis | which features need a biophysical substrate |

Output: feature × signature necessity matrix.

### Statistics
20 graph realizations × 5 input seeds × 5 graph types × 3 matchings × 2 models × 2 drive regimes = 6000 simulations. Two-way ANOVA (graph × matching) with realization-level random effect per signature. Bonferroni across 3 signatures. Cohen's d ≥ 0.8 required for substantive claim.

## 2-4 week pilot

**Goal:** binary go/no-go on whether NWS and Snudda-MSN yield distinguishable assembly switching.

- **Week 1:** Install Snudda + Docker; generate 10k network; extract 500-MSN subvolume; write `graph_build.py` adapter returning {NWS, Snudda-subgraph}.
- **Week 2:** Implement Ponzi-Wickens NMF + dwell-time pipeline; validate against Ponzi-Wickens 2010 random asymmetric reproduction.
- **Week 3:** Run STR on NWS-500 and Snudda-500, 10 realizations each, matched firing rate, 30 s sim, regime A drive.
- **Week 4:** KS test on dwell-time distributions; transition rates.

**Falsification criterion:** Cliff's δ < 0.8 between NWS and Snudda → publish as Brief Communication ("Striatal assembly switching is robust to connectivity topology") and stop. Either branch publishes.

## 3-6 month plan

| Month | Milestone |
|---|---|
| 1 | Pilot complete; Snudda extraction released as reusable script; MS-rewire, Gamma-kernel, modular-D1/D2 constructors with size/degree unit tests |
| 2 | Full 6000-sim battery on cluster. **Vectorize STR's per-neighbor Python loop** (`update_functions.py:87-90`) — currently O(N×K) Python; sparse adjacency × sigmoid(V) gives 10-50× speedup |
| 3 | Petermann/Plenz pipeline (avalanche-modulated drive + correlation distribution + Clauset). Firing-rate KS pipeline |
| 4 | Feature × signature matrix; sensitivity to matching protocol |
| 5 | Writeup; 6 figures (battery schematic, three signatures, necessity matrix, LIF vs STR axis) |
| 6 | Submission |

## Target venue

| Venue | Acceptance odds | Rationale |
|---|---|---|
| Network Neuroscience | ~50% | Gal/Reimann/Markram 2020 + Carannante 2024 both there |
| PLOS Comp Biol | ~30% | Similar methods bar; field-of-view fits |
| eLife | ~25% | Slower; preprint 99402 precedent |

Avoid: J Neurosci (too theoretical without electrophys), Front Comp Neurosci (Belić already there).

## Risk register

1. **Kotaleski-lab releases Carannante-dynamics extension in 6 months** (~30% probability). Mitigations: speed (submit by month 6); LIF/STR axis they won't run (Snudda is multi-compartmental NEURON); email Hjorth/Kotaleski early — collaboration > collision; cite Carannante 2024 generously.
2. **Pilot returns no NWS-vs-Snudda difference** (~20%). Pivot to Brief Communication; still publishable.
3. **Snudda extraction infeasible in time** (~15%). Fall back on synthetic distance-dependent calibrated to Hjorth 2020 connection probabilities (what Belić 2024 did).
4. **STR adaptive-dt heuristic pathological on heavy-tailed degree distributions** (~25%). Hard dt floor; sanity-check voltage bounds; switch to fixed small dt if needed.
5. **Reviewer demands real EM connectome** (~15%). Reference 2025 songbird basal-ganglia connectome; argue Snudda is the standard in-silico striatum.

## Go/no-go

**Go.** No Kotaleski-lab preprint from late 2025/early 2026 covers this framing. Snudda public repo confirmed inactive on null-models. Move quickly.

---

# Shared infrastructure and the integrator fork

## The integrator tension

The three proposals make incompatible demands on the integrator:

- **#1 (AHP reservoir):** requires **fixed dt**. STR and LIF on different adaptive dt grids per condition confounds the comparison fatally. 1-day code change.
- **#2 (dt-as-instrument):** requires the **existing adaptive dt** — it IS the experiment.
- **#3 (connectome atlas):** dt-agnostic, but adaptive heuristic may be pathological on heavy-tailed degree distributions (Snudda subgraphs); may need hard dt floor.

These are genuinely separate studies that cannot share the same codebase fork without managing this carefully. Recommend branching (`feature/fixed-dt-reservoir`, `feature/dt-instrument`, `feature/connectome-atlas`).

## Shared infrastructure week — commits to no proposal

Week 0 work that benefits all three proposals:

1. Fix `N=500, K=8, P=0.01` as production defaults in `const.py:43-45`. Current `N=2` is a debug-only setting.
2. Vectorize the per-neighbor loop in `update_state_STR()` at `update_functions.py:87-90` and `update_state_LIF()` at `:19-22`. Replace Python `for k in G.neighbors(j)` with sparse adjacency × sigmoid(V). 10-50× speedup. Math unchanged.
3. Add a `fixed_dt_mode` Boolean flag in `const.py` (default False, retains current adaptive behavior). Keep `dt_list` recording in both modes.
4. Decide STR spike-reset policy: subthreshold-continuous (citable to Pyle & Rosenbaum 2019) or add proper reset. Document the decision in `update_functions.py`.
5. Expose `const.dt_list` to a CSV/HDF5 writer in `run.py`.
6. Refactor `graph_build.py` so `graph_build(graph_type=...)` accepts any of `{nws, snudda, ms_rewire, gamma_kernel, modular}`. This sets up #3 without committing to it.
7. Add a `metrics/` module with reservoir-readout (#1) and EWS-detector (#2) interfaces.

After Week 0, the three pilots can run in parallel branches.

## Recommended sequencing

| Week | Activity |
|---|---|
| 1 | Shared infrastructure (no commitments) |
| 2 | Pilot #2 (cheapest, most independent) — kill or go |
| 3-4 | Pilot #1 (LIF-het control is make-or-break) — kill or go |
| 4-5 | Pilot #3 (Snudda install can run in background during #1 compute) — kill or go |
| 6 | Commit to surviving proposal(s); fork; begin full project |

By Week 6, you know which has a real paper in it.

## If only one project is possible

- **Lowest risk / safest 1-paper bet:** #1 (AHP reservoir) — proven methodology, mature reservoir field, but the LIF-het control might kill the headline.
- **Highest novelty / most original contribution:** #2 (dt-as-instrument) — the only proposal the field has not framed before. Cheapest to pilot.
- **Highest publishability ceiling / most biological:** #3 (connectome atlas) — real striatum, Network Neuroscience precedent, but scoop window is closing.

---

# Files to touch first

| File | Section | Change |
|---|---|---|
| `const.py:43-45` | All proposals | Set N=500, K=8, P=0.01 as production defaults |
| `const.py` (new lines) | #1 and #2 | Add `fixed_dt_mode` boolean and `fixed_dt_value` |
| `update_functions.py:87-90` | All proposals | Vectorize STR neighbor sum (sparse adj × sigmoid(V)) |
| `update_functions.py:19-22` | All proposals | Same for LIF |
| `update_functions.py:39-40` | #1 and #3 | Decide and document STR spike-reset policy |
| `graph_build.py` | #3 | Refactor to `graph_build(graph_type=...)` interface |
| `run.py` | #1 | Add per-step voltage state-vector logging for ridge readout |
| `run.py` | #2 | Add CSV/HDF5 dump of `const.dt_list` |
| `metrics/` (new directory) | #1 | Ridge regression module with LOO-CV λ selection |
| `metrics/` (new directory) | #2 | EWS detector pipeline (variance, AC(1), spectral entropy, dt-based) |
| `update_functions.py` (LIF) | #1 | Add per-neuron g_L distribution; add ALIF variant |

---

# Citation list (all real, all verified)

## Reservoir / adaptation
- Bernacchia, Seo, Lee, Wang (2011). *Nature Neuroscience* 14:366. https://www.nature.com/articles/nn.2752
- Salaj, Subramoney, Bellec, Legenstein, Maass (2021). *eLife* 10:e65459. https://elifesciences.org/articles/65459
- Perez-Nieves, Goodman et al. (2021). *Nature Communications* 12:5791. https://www.nature.com/articles/s41467-021-26022-3
- Bellec, Salaj, Subramoney, Legenstein, Maass (2018). NeurIPS / arXiv:1803.09574. https://arxiv.org/abs/1803.09574
- Shi, Engelken, Sompolinsky, Wolf (2023). *eLife* 12:e86552. https://elifesciences.org/articles/86552
- Toledo-Suárez, Duarte, Morrison (2014). *Front Comput Neurosci* 8:130. https://www.frontiersin.org/articles/10.3389/fncom.2014.00130
- Cavallari, Panzeri, Mazzoni (2014). *Front Neural Circuits* 8:12. https://www.frontiersin.org/articles/10.3389/fncir.2014.00012
- Boosting Reservoir Computing with Brain-Inspired Adaptive Dynamics (2025). *Nature Communications*. https://www.nature.com/articles/s41467-025-64978-8
- Dambre, Verstraeten, Schrauwen, Massar (2012). Information processing capacity. *Sci Rep* 2:514.
- Legenstein & Maass (2007). *Neural Networks* 20:323-334. Edge of chaos, kernel/generalization rank.
- Pyle & Rosenbaum (2019). *Neural Computation* 31:1430. https://direct.mit.edu/neco/article/31/7/1430/8496

## Numerical analysis / dt-as-observable
- Söderlind, Jay, Calvo (2015). *BIT Numer Math* 55:531-558. https://link.springer.com/article/10.1007/s10543-014-0503-3
- Scheffel (2024). arXiv:2402.17030. https://arxiv.org/abs/2402.17030
- Calvo, Higham, Montijano, Rández (1997). *IMA J Numer Anal*.
- Söderlind (2002). *Numerical Algorithms* 31:281-310.
- Hines & Carnevale NEURON CVODE wrapper.
- Pham, Rein, Spiegel (2024). arXiv:2401.02849. https://arxiv.org/abs/2401.02849
- ShockCast (2025). arXiv:2506.07969. https://arxiv.org/abs/2506.07969

## Lyapunov / EWS / early warning
- Engelken, Wolf, Abbott (2023). *Phys Rev Research*. arXiv:2006.02427. https://arxiv.org/abs/2006.02427
- Engelken (2024). arXiv:2412.21188. https://arxiv.org/abs/2412.21188
- Monteforte & Wolf (2010). *PRL* 105:268104.
- Scheffer et al. (2009). *Nature* 461:53-59.
- Maturana et al. (2020). *Nat Commun* 11:2172.
- Wilkat, Rings, Lehnertz (2019). *Chaos* 29:091104. arXiv:1908.08973.
- Mormann, Andrzejak, Elger, Lehnertz (2007). *Brain* 130:314-333.
- Boettiger & Hastings (2012). *J R Soc Interface* 9:2527.

## Striatum / Snudda / connectome
- Hjorth et al. (2020). *PNAS* 117:9554-9565. https://www.pnas.org/doi/10.1073/pnas.2000671117
- Hjorth, Hellgren Kotaleski, Kozlov (2021). *Neuroinformatics*.
- Carannante, Scolamiero, Hjorth, Kozlov, Kumar, Chacholski, Hellgren Kotaleski (2024). *Network Neuroscience* 8:1149-1172. https://direct.mit.edu/netn/article/8/4/1149
- Frost Nylén et al. (2023). *PNAS* 120:e2313058120.
- Frost Nylén/Grillner et al. (2025). *PNAS*.
- Thompson et al. (2025). *PNAS* 122:e2528602122.
- Belić et al. (2024). *Front Comput Neurosci* 18:1410335. https://www.frontiersin.org/articles/10.3389/fncom.2024.1410335
- Yim, Aertsen, Kumar (2017). *eNeuro* 4:ENEURO.0348-16. https://www.eneuro.org/content/4/4/ENEURO.0348-16.2017
- Spreizer, Aertsen, Kumar (2019). *PLOS Comp Biol* 15:e1007432.
- Bahuguna, Aertsen, Kumar (2015). *PLOS Comp Biol* 11:e1004233.
- Burke, Rotstein, Alvarez (2017). *Neuron* 96:267-284.
- Ponzi & Wickens (2010). *J Neurosci* 30:5894-5911.
- Ponzi & Wickens (2013). *PLOS Comp Biol* 9:e1002954.
- Klaus & Plenz (2016). *PLOS Biology* 14:e1002582.
- Wilson & Kawaguchi (1996). *J Neurosci* 16:2397.

## Null-model methodology / cortical precedent
- Gal, López-Cruz, Reimann, Markram et al. (2020). *Network Neuroscience* 4:798-822. https://direct.mit.edu/netn/article/4/3/798
- Reimann et al. (2017). *Front Comput Neurosci* 11:48.
- Vasa & Misic (2022). *Nat Rev Neurosci* 23:493-504.
- Betzel & Bassett (2017). *J R Soc Interface*.
- Sizemore et al. (2018). *J Comput Neurosci* 44:115-145.
- Hanson et al. (2024). *Nat Comput Sci*.
- Milo et al. (2003). On the uniform generation of random graphs with prescribed degree sequences. arXiv:cond-mat/0312028.
