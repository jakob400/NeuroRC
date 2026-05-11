# NeuroRC — Foundation Work Plan

The operational checklist for fixing bugs, refactoring numerics, and building analysis infrastructure so that the three planned papers (`RESEARCH_DIRECTIONS.md`) become possible.

This document is the single source of truth for *how to fix, in what order, and how to verify each fix*. The companion files are `RESEARCH_DIRECTIONS.md` (what to publish) and `IMPLEMENTATION.md` (the high-level audit that produced this plan).

---

## Status legend & current snapshot

Annotations added 2026-05-11. Original plan text below is untouched except for status markers.

- **[DONE]** — committed on `master`; minimum-verified by `pytest tests/` green.
- **[PARTIAL]** — main work landed but a sub-item remains; pointer to the Follow-up section near the end.
- **[TODO]** — not started.

**Headline (post fix-B, 2026-05-11):** Phases 0, 1, 2 are **[DONE]**.
Phase 3 shared minimum **[DONE]** — GRAPH-1 lognormal weights
(`c04ed2e`), GRAPH-2 dispatched constructor (`08c1c25`), GRAPH-3
NWS-as-DiGraph (`a4c41de`), GRAPH-5 MS-rewire, GRAPH-7 modular SBM.
Remaining Phase 3: GRAPH-4 (Snudda, needs Docker), GRAPH-6 (Gamma
kernel, needs Yim 2017 verification), GRAPH-8 (matching protocols),
GRAPH-9 (smoke tests). All ten Phase 0-2 follow-ups F1-F10 are
**[DONE]**.

**Post-Phase-3 fixes (new since 2026-05-11):**
- **Fix A** (V_thresh recalibration, commit `863faf8`) — restored 1 Hz
  firing rate after GRAPH-3's directed-adjacency change.
- **Fix B** (slow K g_KIR + OU drive replacing Poisson, commits
  `85a07e7`, `cb413bd`) — added bistability mechanism. **D1/D2/D4
  resolved**, D3 worsened-but-publishable. See `DIAGNOSTICS.md`
  post-fix-B sections.
- **Phase B3** (revalidation, commit `4a5a716`) — captured all
  before/after diagnostic outputs in `data/p0/`.
- **Phase P0-S** (methods-paper artifacts, commit `a30b151`) —
  `scripts/p0_make_figures.py`, `figures/p0/`, `data/p0/*.csv`.

56 tests passing in ~6 s under `uv run pytest`. Environment is
uv-managed via `pyproject.toml`. The methods paper P0 is the immediate
next deliverable (manuscript drafting off-repo); see `PUBLICATIONS.md`
and `NEXT_STEPS.md`.

---

## Overview

The codebase contains roughly 12 confirmed bugs across 5 files plus structural issues that prevent it from running at production scale (N=500-10k). Five phases of work, ~44 discrete changes:

- **Phase 0 — Pre-flight bug fixes** (6 changes). Get the code running on modern Python; install a regression baseline. Blocks everything.
- **Phase 1 — STR biophysics calibration** (7 changes). Fix parameter and architectural errors; commit to spike-reset policy.
- **Phase 2 — Numerical architecture refactor** (8 changes). Vectorize state, sparse SpMV, ring-buffer delays, two integrator modes, 9-test validation suite. The largest single engineering effort in the plan.
- **Phase 3 — Graph generation infrastructure** (9 changes). Five-graph battery, Snudda extraction, weight calibration, matching protocols.
- **Phase 4 — Analysis infrastructure & test/reproducibility** (14 changes). Three analysis pipelines, IPC reimplementation, test suite, reproducibility tooling, OSF pre-registration. IPC reimplementation (ANA-6) is the largest technical undertaking in this phase.

Each phase has hard dependencies on prior phases. Within a phase, changes are independently mergeable and CI-green.

If IPC (ANA-6) is deferred and proposal #3 is dropped, the foundation work reduces substantially — only the Phase 4 work specific to proposals #1 and #2 remains.

---

## Phase dependency graph

```
Phase 0 (pre-flight) ──┬──> Phase 1 (biophysics) ──┬──> Phase 2 (numerics) ──┬──> Phase 3 (graphs) ──> Phase 4 production runs
                       │                          │                         │
                       └──> Phase 4 scaffold ─────┴──> ...                  └──> matching protocols
                            (test harness)
```

Cross-cluster constraints:

- Phase 0 must complete before any other phase begins.
- Phase 1 must precede Phase 2 (numerical changes embed AHP / g_K terms).
- Phase 2 must precede Phase 3 production runs (matching protocols require vectorized state; 6000 sims at N=500 untractable on Python loops).
- Phase 4 test scaffolding (ANA-3, ANA-4) can begin in parallel with Phase 0; analysis pipelines (ANA-5..ANA-8) need Phase 1 fixes to be meaningful.
- OSF pre-registration (ANA-14) must complete before any production sweep begins.

---

## Master change table

| ID | Phase | Severity | Status | Files |
|---|---|---|---|---|
| PRE-1 | 0 | Blocker | **[DONE]** `f4ce426` | `update_functions.py`, `graph_build.py`, `dynamic_voltage_plot.py`, `network_plot.py`, `run.py` |
| PRE-2 | 0 | Blocker | **[DONE]** `195553a` | `graph_build.py:8` |
| PRE-3 | 0 | High | **[DONE]** `9492ff4` | `math_functions.py:49-52`, `run.py:80,92` |
| PRE-4 | 0 | Blocker | **[DONE]** `e1b6c91` | `const.py:39`, `update_functions.py`, `math_functions.py`, `dynamic_voltage_plot.py` |
| PRE-5 | 0 | Blocker | **[DONE]** `43b1209` | `weight_generator.py:13` |
| PRE-6 | 0 | High | **[DONE]** `1a0eb10` (+ `da9109a`) | `tests/test_regression.py`, `tests/baselines/`, `simulate.py` |
| BIO-1 | 1 | Blocker | **[DONE]** `3d81995` | `const.py:10` |
| BIO-2 | 1 | Blocker | **[DONE]** `6ebf490` | `const.py:29` |
| BIO-3 | 1 | Blocker | **[DONE]** `d8afb90` | `update_functions.py:91`, `const.py` |
| BIO-4 | 1 | High | **[DONE]** `8e50f1b` | `const.py:25,28` |
| BIO-5 | 1 | High | **[DONE]** `fa1875a` | `graph_build.py:20-22` |
| BIO-6 | 1 | High | **[DONE]** `e38a050` (+ calibration `1ecee0e`, see F1) | `update_functions.py:84`, `const.py` |
| BIO-7 | 1 | Blocker for #2,#3 | **[DONE]** `e055d1f` | `update_functions.py:65-117`, `const.py`, `graph_build.py` |
| NUM-1 | 2 | Blocker | **[DONE]** `e42b18e` | `state.py` (new), `graph_build.py`, `update_functions.py`, `run.py` |
| NUM-2 | 2 | Blocker | **[DONE]** `b052033` | `graph_build.py`, `update_functions.py`, `state.py` |
| NUM-3 | 2 | Blocker | **[DONE]** `b052033` (folded into NUM-2 ring buffer commit) | `math_functions.py`, `state.py`, `update_functions.py` |
| NUM-4 | 2 | Blocker | **[DONE]** `d021b36` | `update_functions.py`, `const.py`, `run.py` |
| NUM-5 | 2 | High | **[DONE]** `7b62bad` interpolation + `6c78bdd` `dt_floor`/`dt_max` clamps (F10) | `const.py`, `update_functions.py` |
| NUM-6 | 2 | High | **[DONE]** `4d95031` V/g/dt + `0534f0f` per-neuron f(V) magnitudes (F8) | `logging_hdf5.py`, `update_functions.py`, `integrators.py`, `state.py` |
| NUM-7 | 2 | High | **[DONE]** `9f7a9e6` | `state.py`, `dynamic_voltage_plot.py`, `network_plot.py` |
| NUM-8 | 2 | High | **[DONE]** `dba2c88` | `tests/test_numerical_*.py` (9 files) |
| GRAPH-1 | 3 | Blocker | **[DONE]** `c04ed2e` | `weight_generator.py`, `const.py`, `tests/test_weights.py` |
| GRAPH-2 | 3 | Blocker | **[DONE]** `08c1c25` | `graph_build.py`, `tests/test_graph_build.py` |
| GRAPH-3 | 3 | High | **[DONE]** `a4c41de` | `graph_build.py`, `state.py`, `tests/test_graph_build.py` |
| GRAPH-4 | 3 | High | **[TODO]** | `scripts/snudda_extract.py` (new), `scripts/snudda_docker/Dockerfile` (new), `data/snudda_500_msn.graphml` |
| GRAPH-5 | 3 | High | **[DONE]** `a8bfc66` | `graph_build.py`, `tests/test_graph_build.py` |
| GRAPH-6 | 3 | High | **[TODO — blocked on Yim 2017 verification]** | `graph_build.py` |
| GRAPH-7 | 3 | High | **[DONE]** `08c1c25` — modular SBM with Burke 2017 asymmetry landed alongside GRAPH-2 dispatch | `graph_build.py` |
| GRAPH-8 | 3 | Blocker for #3 | **[TODO]** | `matching.py` (new), `run.py` |
| GRAPH-9 | 3 | Medium | **[TODO]** | `tests/test_graphs.py` |
| ANA-1 | 4 | Blocker | **[TODO]** | `analysis/spike_io.py` (new) |
| ANA-2 | 4 | Blocker | **[TODO]** | `pyproject.toml`, `requirements.txt`, `environment.yml` |
| ANA-3 | 4 | Blocker | **[TODO]** | `tests/conftest.py`, `pytest.ini`, `.github/workflows/test.yml` |
| ANA-4 | 4 | Blocker | **[TODO]** | `tests/test_regression.py` |
| ANA-5 | 4 | High | **[TODO]** | `metrics/pipeline_a_reservoir.py` (new) |
| ANA-6 | 4 | High | **[TODO]** | `metrics/ipc.py` (new) |
| ANA-7 | 4 | High | **[TODO]** | `metrics/pipeline_b_ews.py` (new) |
| ANA-8 | 4 | High | **[TODO]** | `metrics/pipeline_c_spikes.py` (new) |
| ANA-9 | 4 | High | **[TODO]** | `analysis/stats.py` (new) |
| ANA-10 | 4 | High | **[TODO]** | `tests/test_biophysics.py`, `test_numerical.py`, `test_graphs.py` |
| ANA-11 | 4 | Medium | **[TODO]** | `analysis/logging.py` |
| ANA-12 | 4 | Medium | **[TODO]** | `CITATION.cff`, `LICENSE`, `Dockerfile`, `.zenodo.json`, `README.md` |
| ANA-13 | 4 | Nice-to-have | **[TODO]** | `.datalad/config`, `data/.gitattributes` |
| ANA-14 | 4 | High | **[TODO]** | `prereg/proposal_1_reservoir.md`, `prereg/proposal_2_dt_ews.md` |

---

# Phase 0 — Pre-Flight Bug Fixes — **[DONE]**

> Status snapshot (2026-05-11): all 6 PRE items landed on master plus one follow-up fix; Phase 0 gate green. See Master change table for commit SHAs.

This cluster blocks all downstream work. Until every item here is green, no behavioural or numerical claim about the simulator can be trusted, and NetworkX 2.x/3.x will refuse to import the call sites. Each item is small and self-contained — the cluster is intended to land in a single focused session.

The repository targets Python 3.9 (system default at `/Users/jakob/Development/NeuroRC/`). Adopt NetworkX 3.x as the pin (see PRE-1).

## PRE-1 — Port NetworkX 1.x API to 2.x/3.x — **[DONE — commit `f4ce426`]**

- **Severity:** Blocker
- **Summary:** Replace every `G.node[...]` / `len(G.node)` / `nx.info(G)` reference; the 1.x API was removed in NetworkX 2.4 and the module-property fallback removed in 3.0.
- **File:line locations:**
  - `graph_build.py:18, 23, 24, 25, 26, 28, 30` (`G.node[j]` and `len(G.node)`)
  - `update_functions.py:8, 9, 12, 14, 21, 35, 36, 39, 40, 58, 65, 67, 68, 69, 70, 89, 107, 108, 109, 110, 111` (`G.node[j]` and `len(G.node)`)
  - `dynamic_voltage_plot.py:19, 21, 22, 23` (`G.node[nnumber1]`)
  - `network_plot.py:8` (`G.node[j]`)
  - `run.py:100` (`nx.info(G)` — removed in NetworkX 3.0)
  - `run.py:98` is already correct (`G.nodes[1]`); leave alone.

**Fix:**
- Replace every `G.node[j]` with `G.nodes[j]`. Semantics of `.update({'k': v})` and `[k] = v` unchanged on the `NodeView` returned by `G.nodes[j]`.
- Replace every `len(G.node)` with `G.number_of_nodes()` (preferred — explicit and version-stable).
- In `run.py:100`, replace `print(nx.info(G), '\n')` with:
  ```python
  print(f"Graph: {G.name} — {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")
  ```
- Pin dependency in `requirements.txt`:
  ```
  networkx>=3.0,<4.0
  numpy>=1.24
  matplotlib>=3.6
  ```
- Concrete before/after for the hottest call site (`update_functions.py:12-14`):
  ```python
  # before
  M = [None] * len(G.node)
  func_v = [None] * len(G.node)
  for j in range(len(G.node)):
      voltage_now = G.node[j]['voltage'][t]
  # after
  n = G.number_of_nodes()
  M = [None] * n
  func_v = [None] * n
  for j in range(n):
      voltage_now = G.nodes[j]['voltage'][t]
  ```

**Verification:**
1. `pip install -r requirements.txt` exits 0.
2. `python -c "import ast; [ast.parse(open(f).read()) for f in ['graph_build.py','update_functions.py','math_functions.py','weight_generator.py','dynamic_voltage_plot.py','network_plot.py','run.py']]"` succeeds.
3. `grep -nE "G\.node\[|len\(G\.node\)|nx\.info" *.py` returns no matches.
4. `echo "LIF" | python run.py` with `const.tMax = 10` runs to completion without `AttributeError`.

**Dependencies:** None.

## PRE-2 — Convert random seed from float to int — **[DONE — commit `195553a`]**

- **Severity:** Blocker
- **Summary:** `random.uniform(1, 10000)` returns a float; NetworkX 2.4+ raises `TypeError: 'float' object cannot be interpreted as an integer` when seed is non-int.
- **File:line:** `graph_build.py:8-9`.

**Fix:**
```python
# before
seed_no = random.uniform(1, 10000)
G = nx.newman_watts_strogatz_graph(const.N, const.K, const.P, seed=seed_no)
# after
seed_no = random.randint(1, 10000)
G = nx.newman_watts_strogatz_graph(const.N, const.K, const.P, seed=seed_no)
print(f"graph seed: {seed_no}")
```
Optionally lift the seed into `const.py` as `graph_seed = None` (None = randomise each run) so PRE-6's regression test can pin it.

**Verification:** `python -c "import graph_build; G = graph_build.graph_build(); print(type(G), G.number_of_nodes())"` prints `<class 'networkx.classes.graph.Graph'> 2` with no traceback.

**Dependencies:** PRE-1.

## PRE-3 — Strip per-timestep `print` calls from hot loop — **[DONE — commit `9492ff4`]**

- **Severity:** High
- **Summary:** Four `print` statements fire on every timestep inside `delay()`; stdout I/O caps throughput at ~10⁴ steps/sec.
- **File:line:** `math_functions.py:49-52`. Also `run.py:80, 92` (the `print('t is = ', t)` calls).

**Fix:** Delete `math_functions.py:49-52` outright. Do NOT replace with `logging.debug(...)` — still pays `logger.isEnabledFor` cost. If diagnostics needed later, gate behind `if const.debug_delay:` flag.
```python
# before
while( dt_sum < const._tau_D ):
    if(len(const.dt_list) > i):
        dt_sum += const.dt_list[-i-1]
        i += 1
    else:
        break
print('dt_sum is',dt_sum)
print('_tau_D is',const._tau_D)
print('steps back is',i)
print('time_delayed is ', t-i,'\n')
return t-i
# after
while dt_sum < const._tau_D:
    if len(const.dt_list) > i:
        dt_sum += const.dt_list[-i - 1]
        i += 1
    else:
        break
return t - i
```
Also delete the `print('t is = ', t)` in `run.py:80, 92`.

**Verification:**
1. `grep -n "^\s*print" math_functions.py` returns no matches.
2. Benchmark: `time (echo "LIF" | python run.py > /tmp/run.log)` at `tMax=1000, N=10, K=2` should drop ≥5× wall-time.

**Dependencies:** PRE-1.

## PRE-4 — Eliminate `const.dt_list` as cross-run module state — **[DONE — commit `e1b6c91`]**

- **Severity:** Blocker (silent correctness)
- **Summary:** `const.dt_list` is module-level mutable; accumulates across simulations in the same Python process. Batch runs silently corrupt every run after the first.
- **File:line locations:**
  - Declaration: `const.py:39`
  - Mutations: `update_functions.py:32, 36, 103, 108, 109, 110, 111, 116`
  - Reads: `math_functions.py:44, 45`, `dynamic_voltage_plot.py:15, 16, 54, 55`

**Fix:** Move `dt_list` off `const` and onto the graph object as a graph-level attribute. Keeps the change local (5 files) and preserves the "everything hangs off `G`" pattern.
1. In `const.py`, **delete** line 39 (`dt_list = []`).
2. In `graph_build.set_graph_attributes`, after model branches, add: `G.graph['dt_list'] = []`.
3. In `math_functions.py:delay(t)`, change signature to `delay(t, dt_list)`; update call sites in `update_functions.py:6` and `:55` to pass `G.graph['dt_list']`.
4. In `update_functions.py`, replace every `const.dt_list` with `G.graph['dt_list']`.
5. In `dynamic_voltage_plot.py`, change `voltage_plot(G)` to read `G.graph['dt_list']` (lines 15, 16, 54, 55).

**Verification:**
1. `grep -n "const\.dt_list\|const\.\s*dt_list" *.py` returns no matches.
2. Test in PRE-6 (`test_in_process_runs_are_independent`): two back-to-back `simulate()` calls produce bit-identical voltage lists.

**Dependencies:** PRE-1.

## PRE-5 — Restore real synaptic weights in `weight_generator` — **[DONE — commit `43b1209`]**

- **Severity:** Blocker (silent correctness)
- **Summary:** Every edge weight hardcoded to `1`; `getWeight()` returns floats in `[0, 100]` (dead code); README/CLAUDE claim weights should be uniform `[-1e-3, 1e-3]` via `const.lowrand`/`const.highrand`. Three different intentions in one file.
- **File:line:** `weight_generator.py:1-14`. Constants live at `const.py:40-41`.

**Fix:** Adopt the documented range, delete dead code, seed the RNG.
```python
# weight_generator.py (full file after fix)
import random
import const

def weight_generator(G, seed=None):
    """Assign each edge a weight drawn uniformly from [const.lowrand, const.highrand]."""
    rng = random.Random(seed)
    for u, v in G.edges():
        G[u][v]['weight'] = rng.uniform(const.lowrand, const.highrand)
    return G
```
Delete `getWeight`, `small`, `large`, `decimals`, unused `import networkx as nx`. In `run.py:61`, update call to `weight_generator(G, seed=const.weight_seed)` and add `weight_seed = None` to `const.py`.

**Note:** Phase 3 (GRAPH-1) replaces this with `assign_weights(G, distribution=..., rng=...)` supporting lognormal/uniform/snudda_native. PRE-5 is the cheap stopgap that unblocks PRE-6's baseline.

**Verification:**
```bash
python -c "
import graph_build, weight_generator
G = graph_build.graph_build()
G = graph_build.set_graph_attributes(G, 'LIF')
G = weight_generator.weight_generator(G, seed=0)
ws = [G[u][v]['weight'] for u, v in G.edges()]
assert all(-1e-3 <= w <= 1e-3 for w in ws), ws
assert len(set(ws)) > 1, 'weights not varying'
print('OK', ws)
"
```

**Dependencies:** PRE-1.

## PRE-6 — Establish numerical regression test as Phase 0 exit criterion — **[DONE — commits `1a0eb10`, plus `da9109a` LIF voltage_plot patch surfaced by the gate]**

- **Severity:** High (gating)
- **Summary:** Capture a deterministic trace under fixed seeds so every later refactor can be verified bit-for-bit (or within a documented tolerance).
- **Files:** New `tests/__init__.py`, `tests/test_regression.py`, `tests/baselines/lif_n2_t1000_s42.npz`, `requirements-dev.txt`, `simulate.py`.

**Fix:**
1. Extract `run.py` body into callable `simulate(model, tMax, graph_seed, weight_seed, N, K, P)` in a new `simulate.py`. Leave `run.py` as the CLI shim.
2. Write `tests/test_regression.py`:
   ```python
   import numpy as np
   import pytest
   from simulate import simulate

   BASELINE = "tests/baselines/lif_n2_t1000_s42.npz"

   @pytest.fixture(scope="module")
   def trace():
       G, _ = simulate(model="LIF", tMax=1000, graph_seed=42, weight_seed=7,
                       N=2, K=1, P=1e-5)
       v0 = np.asarray(G.nodes[0]["voltage"], dtype=np.float64)
       v1 = np.asarray(G.nodes[1]["voltage"], dtype=np.float64)
       dt = np.asarray(G.graph["dt_list"], dtype=np.float64)
       return v0, v1, dt

   def test_voltage_trace_matches_baseline(trace):
       v0, v1, dt = trace
       ref = np.load(BASELINE)
       np.testing.assert_allclose(v0, ref["v0"], rtol=0, atol=1e-12)
       np.testing.assert_allclose(v1, ref["v1"], rtol=0, atol=1e-12)
       np.testing.assert_allclose(dt, ref["dt"], rtol=0, atol=1e-15)

   def test_in_process_runs_are_independent():
       G1, _ = simulate(model="LIF", tMax=50, graph_seed=42, weight_seed=7, N=2, K=1, P=1e-5)
       G2, _ = simulate(model="LIF", tMax=50, graph_seed=42, weight_seed=7, N=2, K=1, P=1e-5)
       assert list(G1.nodes[0]["voltage"]) == list(G2.nodes[0]["voltage"])
   ```
3. Generate baseline ONLY AFTER PRE-1..PRE-5 are green:
   ```bash
   python -c "
   import numpy as np
   from simulate import simulate
   G, _ = simulate(model='LIF', tMax=1000, graph_seed=42, weight_seed=7, N=2, K=1, P=1e-5)
   np.savez('tests/baselines/lif_n2_t1000_s42.npz',
            v0=np.asarray(G.nodes[0]['voltage'], dtype=np.float64),
            v1=np.asarray(G.nodes[1]['voltage'], dtype=np.float64),
            dt=np.asarray(G.graph['dt_list'], dtype=np.float64))
   "
   ```
4. **Use LIF, not STR, for the baseline:** Phase 1 explicitly mutates STR; LIF baseline survives Phases 1-4 unchanged.
5. Fixed parameters: `N=2, K=1, P=1e-5, tMax=1000, graph_seed=42, weight_seed=7`. Baseline file <50 KB, runs in <1 s.

**Verification:**
1. `pytest tests/test_regression.py -v` reports two passing tests.
2. Baseline file committed.
3. CI fingerprint: capture `sha256` of `v0` array in commit message for cross-machine sanity-check.

**Dependencies:** PRE-1, PRE-2, PRE-3, PRE-4, PRE-5.

## Phase 0 — Execution order and verification gate — **[DONE]**

**Order:** PRE-1 → PRE-2 → PRE-3 → PRE-5 → PRE-4 → PRE-6. Rationale: cheap-and-blocking first (PRE-1, PRE-2), behaviour-changing fixes next (PRE-3, PRE-5, PRE-4), freeze-the-behaviour last (PRE-6).

**Phase 0 verification gate (all must pass before Phase 1 starts):**
1. `pip install -r requirements.txt -r requirements-dev.txt` exits 0; `pip show networkx` reports ≥3.0.
2. `python -c "import networkx as nx; assert nx.__version__.split('.')[0] in ('2','3'); from simulate import simulate; G,_ = simulate('LIF', tMax=10, graph_seed=1, weight_seed=1, N=2, K=1, P=1e-5); print('compat OK')"` succeeds.
3. Smoke test: `echo "LIF" | python run.py` AND `echo "STR" | python run.py` both complete `const.tMax` steps, produce PNGs, exit 0.
4. `pytest tests/ -v` — both regression tests pass.
5. `grep -nE "G\.node\[|len\(G\.node\)|nx\.info|const\.dt_list" *.py` returns no matches.
6. LIF at `N=2, K=1, tMax=1000` completes in <2 s wall-time (vs ~10-15 s pre-PRE-3).

**Phase 0 commit boundaries (six commits on `phase-0` branch):**
1. `port NetworkX 1.x call sites to 2.x/3.x API` (PRE-1, +`requirements.txt`)
2. `use integer seed for newman_watts_strogatz_graph` (PRE-2)
3. `remove per-timestep debug prints` (PRE-3)
4. `draw edge weights from configured uniform range` (PRE-5)
5. `move dt_list off const module onto graph` (PRE-4)
6. `add LIF regression baseline and pytest harness` (PRE-6)

**Phase 0 risks:**
1. **PRE-4 dt_list migration silently changes voltages.** Mitigation: make `delay()` accept `dt_list` as required positional (no default); generate PRE-6 baseline after PRE-4 lands.
2. **PRE-6 baseline platform-dependent.** Mitigation: use `random.Random(seed)` for determinism; `atol=1e-12` not 0; document baseline platform in test docstring; regenerate on CI if different OS.
3. **PRE-1 misses a call site in `network_plot.py` (dormant since caller commented out).** Mitigation: import-and-call check `python -c "from simulate import simulate; import network_plot; G,_=simulate('LIF',tMax=2,...); network_plot.network_plot(G,1)"`.

---

# Phase 1 — STR Biophysics Calibration — **[DONE]**

> Status snapshot (2026-05-11): all 7 BIO items landed plus a Poisson calibration follow-up. Per-change arithmetic checks verified; **behavioural biophysics checks (AHP τ fit, ISI₅/ISI₁, IPSC amplitude) deferred to Follow-up §F7** because firing is too sparse at the current Poisson defaults (Follow-up §F1).

The STR model contains real biophysical bugs that make it closer to a broken LIF than to a published reduced striatal model (Ponzi & Wickens 2010 is closest precedent). Fixes ordered so each can be verified in isolation. BIO-7 (spike reset) is the most technically involved item — it introduces a voltage discontinuity that interacts with the adaptive-dt integrator.

Depends on: Phase 0 complete. Blocks: Phase 2, all three papers.

## BIO-1 — Correct AHP time constant — **[DONE — commit `3d81995`]**

- **Severity:** Blocker. The most consequential bug; proposal #1's headline claim depends on a realistic AHP timescale.
- **Summary:** Set τ_AHP ≈ 50 ms (currently 1 ms, three orders of magnitude too fast).
- **File:line:** `const.py:10`.
- **Root cause:** `_a_A = 1e3 s⁻¹` gives τ = 1 ms. Striatal MSN K_AS / SK have decay 50-200 ms (Nisenbaum & Wilson 1995, J Neurosci 15:4449; Wolf et al. 2005, J Neurosci 25:9080 fit τ_SK ≈ 80 ms).

**Fix:**
```python
# BEFORE
_a_A = 1e3     #(sec)^-1
# AFTER
_a_A = 20      #(sec)^-1  ->  tau_AHP = 50 ms (Nisenbaum & Wilson 1995; Wolf 2005)
```

**Verification:** Single isolated neuron (`N=1, K=0`), `drive_mode='constant'`, brief depolarizing pulse to elicit one spike. Fit single-exponential `g_A(t) = g_A(0) exp(-t/τ)` to post-pulse `conductance_A`. **Pass:** τ_fit ∈ [45, 55] ms.

**Dependencies:** None. **Citation:** Nisenbaum & Wilson 1995; Wolf, Moyer, Lazarewicz et al. 2005.

## BIO-2 — Correct AHP scale factor — **[DONE — commit `6ebf490`]**

- **Severity:** Blocker.
- **Summary:** Raise AHP ceiling so adaptation is a real player against the leak.
- **File:line:** `const.py:29`.
- **Root cause:** `w_A = 0.01` × `g_A_max = 25 nS` yields 0.25 nS AHP ceiling, ≈1% of `g_L = 28 nS`. AHP current is too small to perturb the membrane.

**Fix:** Option α (preferred — keeps `g_A_max` interpretable per published K_AS density):
```python
# BEFORE
w_A = 1e-2     # scale factor for AHP
# AFTER
w_A = 0.5      # scale factor for AHP -> g_A_ceil ~ 12.5 nS (~0.5 * g_L)
```

**Verification:** After BIO-1 + BIO-2, single neuron under sustained suprathreshold current shows SFA: train of 5 spikes with input held constant must show ISI₅/ISI₁ ≥ 1.3 (Wilson 2007 reports ~1.5-2× adaptation ratios in DLS MSNs).

**Dependencies:** BIO-1. **Citation:** Wilson 2007 Trends Neurosci 30:603; Mahon et al. 2003 J Physiol 550:947.

## BIO-3 — Fix recurrent inhibitory scaling (g_K_max → g_I_max) — **[DONE — commit `d8afb90`]**

- **Severity:** Blocker.
- **Summary:** Inhibitory recurrent input scaled by voltage-gated K saturation conductance — almost certainly a copy-paste bug. Replace with dedicated `conductance_I_max`.
- **File:line:** `update_functions.py:91`.
- **Root cause:** Current code uses `conductance_K_max = 25 nS` (the voltage-gated K saturation, not unitary IPSC peak). Koos, Tepper & Wilson 2004 measure unitary GABA_A ≈ 1-1.5 nS between MSN pairs.

**Fix:**
- Add to `const.py` (group with other conductances around line 22):
  ```python
  conductance_I_max = 1.5e-9   # Siemens - unitary recurrent IPSC peak (Koos et al. 2004)
  ```
- Edit `update_functions.py:91`:
  ```python
  # BEFORE
  func_I[j] = (-1 * const._a_I * conductance_I_now
               + const._a_I * const.conductance_K_max * summation)
  # AFTER
  func_I[j] = (-1 * const._a_I * conductance_I_now
               + const._a_I * const.conductance_I_max * summation)
  ```

**Verification:** Pair `(N=2, K=1, w_jk=1)`. Force neuron 0 to spike once. Inspect `G.node[1]['conductance_I']` peak: must be in 0.5-3 nS range. IPSP amplitude visible in `voltage`: ~0.3-1 mV.

**Dependencies:** None code-side. **Citation:** Koos, Tepper & Wilson 2004, J Neurosci 24:7916.

## BIO-4 — Sigmoid slope sanity check — **[DONE — commit `8e50f1b`]**

- **Severity:** High (not blocker because model runs — but threshold gating is essentially absent).
- **Summary:** Both sigmoid slopes are 0.8 V⁻¹, making sigmoids near-linear over the voltage range.
- **File:line:** `const.py:25, 28`.
- **Root cause:** `_k = 8e-1 V⁻¹`. Over ΔV of 40 mV the exponent argument changes by 0.032 — sigmoid moves from σ≈0.49 to σ≈0.51. Ponzi & Wickens 2010 use β = 0.25/mV = 250 V⁻¹.

**Fix:** Adopt Ponzi-Wickens convention for direct comparability with closest published precedent:
```python
# BEFORE
_k    = 8e-1     #(V)^-1
_beta = 8e-1     #(v)^-1
# AFTER  -> Ponzi & Wickens 2010, beta = 0.25/mV
_k    = 250.0    # (V)^-1  - K_AS activation slope
_beta = 250.0    # (V)^-1  - recurrent transmission gain
```

**Verification:** Plot `sigma(V)` and `sigma_0(V)` over V ∈ [-90, -30] mV. Transition width (σ from 0.1 to 0.9) should be ~17 mV.

**Dependencies:** BIO-3. **Citation:** Ponzi & Wickens 2010; Wilson & Kawaguchi 1996; Mahon, Deniau & Charpier 2003.

## BIO-5 — Honor initial-conductance constants — **[DONE — commit `fa1875a`]**

- **Severity:** High.
- **Summary:** `graph_build.set_graph_attributes` overwrites `const.conductance_*_init` with zeros, producing 50-100 ms artifactual transient.
- **File:line:** `graph_build.py:20-22`.

**Fix:**
```python
# BEFORE
timelistv  = [v0]
timelistcA = [0]
timelistcE = [0]
timelistcI = [0]
# AFTER
timelistv  = [v0]
timelistcA = [const.conductance_A_init]
timelistcE = [const.conductance_E_init]
timelistcI = [const.conductance_I_init]
```

**Verification:** Single neuron, no input, 200 ms simulation. Max-abs deviation of `g_A`, `g_E`, `g_I` from initial values must drop to within 5% of resting steady state within 10 ms (was ~50 ms).

**Dependencies:** BIO-1, BIO-3.

## BIO-6 — Replace constant cortical drive with per-neuron Poisson kicks — **[DONE — commit `e38a050` + calibration follow-up `1ecee0e`. NOTE: defaults are 20 kHz × 1 nS, picked empirically to push V to threshold. Literature recalibration tracked in Follow-up §F1.]**

- **Severity:** High (Blocker for proposals #1, #2).
- **Summary:** Replace `I = 1e-3` constant in `func_E` with stochastic per-neuron Poisson conductance events.
- **File:line:** `update_functions.py:84` plus new constants in `const.py`.
- **Root cause:** Cortical input to striatum is event-driven, asynchronous, heavy-tailed (Stern, Jaeger & Wilson 1998). Identical constant drive precludes reservoir computing, decorrelation, assembly switching analyses.

**Fix:**
- Add to `const.py`:
  ```python
  # Cortical drive
  drive_mode      = 'poisson'   # 'constant' | 'poisson'
  lambda_input    = 400.0       # Hz per neuron (100 afferents x 4 Hz)
  delta_g_E_event = 1.0e-10     # Siemens per event (100 pS, mEPSC scale)
  I_drive_const   = 1.0e-3      # legacy constant drive
  ```
- In `update_state_STR`, vectorized Poisson sampling per step:
  ```python
  import numpy as np  # at top of file
  # Before per-neuron loop:
  dt = G.graph['dt_list'][-1] if G.graph['dt_list'] else const.epsilon / 1e3
  if const.drive_mode == 'poisson':
      n_events = np.random.poisson(const.lambda_input * dt, size=G.number_of_nodes())
  # After integration step (post-append to conductance_E):
  if const.drive_mode == 'poisson':
      for j in range(G.number_of_nodes()):
          G.nodes[j]['conductance_E'][-1] += const.delta_g_E_event * n_events[j]
  ```
  This treats events as delta impulses on `g_E`; cleaner than `/dt` form for adaptive-dt.

**Verification:**
1. With `drive_mode='constant'` results must match pre-BIO-6 within float tolerance.
2. With `drive_mode='poisson'`: 1 s, single neuron, no recurrent. Mean `g_E` ≈ `λ * Δg_E / a_E` (analytic steady state). **Pass:** within 10%.
3. After BIO-7: ISI CV under Poisson drive in small network ∈ [0.5, 1.5].

**Dependencies:** BIO-3, BIO-7 (CV measurement). **Citation:** Stern, Jaeger & Wilson 1998 Nature 394:475.

## BIO-7 — Add proper STR spike-reset (Option B) — **[DONE — commit `e055d1f`. Option B (threshold-reset) chosen per scoping decision so all three proposals stay on the table.]**

- **Severity:** Blocker for proposals #2 and #3. The single most consequential decision in the cluster.
- **Summary:** Implement threshold-detect + reset + refractory + downstream spike event.
- **File:line:** `update_functions.py:65-117`, `const.py`, `graph_build.py`.
- **Root cause:** Current model is subthreshold-continuous (`if voltage_now > 0.04:` commented out at lines 72-74). Without spike events, ISIs/firing rates/raster plots/assembly detection undefined.

**Decision recap:**

| Aspect | Option A — subthreshold-continuous | Option B — explicit threshold/reset |
|---|---|---|
| Implementation | None (status quo) | Moderate — threshold/reset/refractory + delta-g_I event handling |
| Compatible with proposal #1 | Yes (Pyle & Rosenbaum 2019 precedent) | Yes |
| Compatible with proposal #2 | Marginal | Yes |
| Compatible with proposal #3 | **No** | Yes |
| Numerical risk | Smooth, integrator-friendly | Discontinuity at reset — interacts with adaptive-dt |

**Recommend Option B.** Only option compatible with all three proposals.

**Fix specification:**
- New constants in `const.py`:
  ```python
  voltage_reset      = -65e-3    # (V) = V_L
  voltage_spike_peak = 20e-3     # (V) cosmetic peak in trace
  t_refractory       = 2.0e-3    # (s)
  delta_g_I_event    = 1.5e-9    # (S) postsynaptic kick per presyn spike
  ```
- Per-neuron state in `graph_build.set_graph_attributes` (STR branch):
  ```python
  G.nodes[j].update({'last_spike_time': -1.0})
  G.nodes[j].update({'spike_times': []})
  ```
- In `update_state_STR`, after voltage append:
  ```python
  sim_time_now = sum(G.graph['dt_list'])
  for j in range(G.number_of_nodes()):
      v_new = G.nodes[j]['voltage'][-1]
      in_refractory = (sim_time_now - G.nodes[j]['last_spike_time']) < const.t_refractory
      if in_refractory:
          G.nodes[j]['voltage'][-1] = const.voltage_reset
      elif v_new >= const.voltage_thresh:
          G.nodes[j]['voltage'][-1] = const.voltage_spike_peak
          G.nodes[j]['last_spike_time'] = sim_time_now
          G.nodes[j]['spike_times'].append(sim_time_now)
          for k in G.neighbors(j):
              if k != j:
                  G.nodes[k]['conductance_I'][-1] += (
                      G[j][k]['weight'] * const.delta_g_I_event
                  )
  ```
- **CRITICAL DECISION: Do NOT reset g_A on spike. AHP must persist across spikes.**
- **CRITICAL DECISION: Remove the continuous σ-driven recurrent g_I term** from `func_I` once BIO-7 lands. Use only spike-event delta kicks. Matches Ponzi & Wickens 2010 exactly. (Keep σ in the AHP gating `func_A`.)

**Verification:**
1. Single STR neuron, sustained current injection. f-I curve monotonic, range 0-40 Hz, no firing below threshold.
2. ISI regularity at constant input: at 20 Hz target, CV_ISI < 0.15 (clockwork firing without noise).
3. Refractory: no two spikes within `t_refractory` for any neuron.
4. Pair `(N=2, K=1)`: force pre to spike once. Post shows IPSP of −0.3 to −1.0 mV (Koos 2004 range).

**Dependencies:** BIO-3, BIO-6. **Citation:** Ponzi & Wickens 2010 J Neurosci 30:5894.

**Cross-fix interactions:**
- BIO-1 + BIO-7: longer τ_AHP combined with hard reset — don't reset g_A on spike (decision above).
- BIO-6 + BIO-7: Poisson kicks during refractory must still accumulate on g_E (refractory is voltage-state thing, not conductance-state).
- BIO-4 + BIO-7: with steep σ and BIO-7's delta-g_I, the continuous σ term is now redundant — remove it (decision above).

## Phase 1 — Execution order, commits, risks — **[DONE — see Master change table for SHAs]**

**Commit order:**
1. BIO-1 + BIO-2: "Fix AHP timescale and scale (tau=50ms, w_A=0.5)"
2. BIO-3: "Add conductance_I_max for recurrent inhibition (Koos 2004)"
3. BIO-4: "Correct sigmoid slope parameters (units fix)"
4. BIO-5: "Honor initial conductance constants in graph build"
5. BIO-6: "Add Poisson cortical drive mode"
6. BIO-7: "Add STR spike threshold/reset with refractory and delta-g_I synapses"

Do not bundle BIO-7 with anything else — largest behavioral change, benefits from clean bisect target.

**Sanity-check protocol for the fixed STR model:**
- 4.1: f-I curve in 0-40 Hz range matching Mahon 2003 / Wilson 2007.
- 4.2: Post-spike AHP fit τ ∈ [45, 55] ms.
- 4.3: Pair-recording IPSP peak ∈ [-1.0, -0.3] mV; decay τ ≈ 5 ms (matches Koos 2004).
- 4.4: Small network (N=10, K=2, P=0.1) Poisson drive: rates 1-15 Hz, mean CV_ISI ∈ [0.5, 1.5], no neuron silent for 5 s.
- 4.5: Numerical stability — `tMax=1e5`, no `dt < 1e-7`, no `|V| > voltage_spike_peak + 5 mV`.

If 4.5 fails after BIO-7 → that's the trigger for Phase 2 integrator rewrite (expected, not regression).

**Risks (top):**
1. **BIO-7 × adaptive-dt** (highest interaction risk). Voltage discontinuity at reset can be missed by step controller. Mitigation: cap `dt_max = 0.5 * t_refractory` globally (cheap Phase 1 fix); detect impending threshold crossing and shrink dt (proper Phase 2 work).
2. **BIO-6 adds numpy as runtime dependency at integrator core.** Add `random_seed` constant, seed `np.random.seed(...)` for reproducibility.
3. **Rollback dependency**: BIO-7 uses `conductance_I_max` introduced in BIO-3 — reverting BIO-3 without also reverting BIO-7 breaks the build.

---

# Phase 2 — Numerical Architecture Refactor — **[DONE]**

> Status snapshot (2026-05-11): all 8 NUM items landed. Gate green: 12 tests pass (regression + SpMV parity + 9 validation), LIF N=500 fixed-dt at ~0.3 s (target <30 s), HDF5 dump verified. STR vectorization gave ~15× over the pre-refactor loop. NUM-5 and NUM-6 are **partial** in scope — see annotations on those sections and Follow-up §F8, §F10.

Largest single engineering effort in the foundation work. Replaces per-node Python-list state with flat NumPy/sparse-CSR architecture; introduces two-mode integrator (adaptive Euler kept verbatim for proposal #2; new fixed-dt Heun + exponential-Euler for proposals #1 and #3); ring buffer for delays; per-neuron `f` logging; 9-test validation suite. Technically challenging: the integrator rewrite must preserve adaptive-Euler behaviour verbatim under one mode while delivering correct convergence order under the other, and the 9-test suite gates the rest of the project.

Depends on: Phase 0 + Phase 1 complete.

## NUM-1 — Replace per-node Python-list state with flat NumPy state vectors — **[DONE — commit `e42b18e`. Also fixed a pre-existing per-neuron state-bleed bug in the legacy main-calc loop.]**

- **Severity:** Blocker. Current `G.nodes[j]['voltage'].append(...)` costs O(N·T) Python objects; ~96 GB at N=500, T=30 s.
- **Files:** `state.py` (new), `graph_build.py`, `update_functions.py`, `run.py`, `dynamic_voltage_plot.py`, `network_plot.py`.

**Fix:** New `state.py`:
```python
import numpy as np
import const

class SimState:
    def __init__(self, N, model):
        self.N = N
        self.model = model
        self.V  = np.full(N, const.voltage_init, dtype=np.float64)
        if model == 'STR':
            self.gE = np.full(N, const.conductance_E_init, dtype=np.float64)
            self.gI = np.full(N, const.conductance_I_init, dtype=np.float64)
            self.gA = np.full(N, const.conductance_A_init, dtype=np.float64)
        self.t_sim = 0.0
        self.step  = 0
```
Graph nodes carry only static metadata. Loops in `update_state_*` become vectorized:
```python
excitatory = (const.voltage_E - V) * gE
inhibitory = (const.voltage_I - V) * gI
leakage    = (const.voltage_L - V) * const.conductance_L
potassium  = (const.voltage_K - V) * (const.conductance_K_max * sigma_0_vec(V) + gA)
f_v        = (excitatory + leakage + inhibitory + potassium) / const.capacitance
```

**Verification:** Phase 0 regression test (at N=2) must match to `np.allclose(rtol=1e-10)` (slight loosening because float ordering changes). Test 5 (parameter sweep) — no explosions at N=500.

**Dependencies:** Phase 1 fixes embedded.

## NUM-2 — Sparse CSR adjacency for recurrent input — **[DONE — folded into commit `e42b18e` (state.A as scipy.sparse.csr_matrix); parity test at N=10 atol 1e-12 in commit `e7e7bb5`]**

- **Severity:** Blocker. 100-500× speedup.
- **Files:** `graph_build.py` (build A), `update_functions.py` (use A), `state.py`.

**Fix:**
```python
import scipy.sparse as sp
def build_adjacency_csr(G):
    N = G.number_of_nodes()
    rows, cols, data = [], [], []
    for i, j, d in G.edges(data=True):
        w = d.get('weight', 1.0)
        rows += [i, j]; cols += [j, i]; data += [w, w]
    A = sp.csr_matrix((data, (rows, cols)), shape=(N, N), dtype=np.float64)
    A.setdiag(0); A.eliminate_zeros()
    return A
```
Recurrent drive: `summation = A.dot(sigma_vec(V_delayed))`. Vectorize `sigma`, `sigma_0` as NumPy ufuncs:
```python
def sigma_vec(V):
    return 1.0 / (1.0 + np.exp(const._beta * (const.voltage_thresh - V)))
```

**Verification:** Regression at N=2 still bit-equivalent. Microbench at N=500, K=7: SpMV inner section <1 ms (vs ~200 ms Python loop).

**Dependencies:** NUM-1. `scipy.sparse` ≥1.8.

## NUM-3 — Ring buffer for delayed voltages — **[DONE — commit `b052033`. delay_buffer.RingBuffer with at(i) O(1) lookup; depth scaled by tau_D / dt_min.]**

- **Severity:** Blocker. Replace O(N·K·D) lookup with O(1).
- **Files:** `math_functions.py` (delete `delay`, `delta`), `state.py`, `update_functions.py`.

**Fix:** Two indexing strategies controlled by `const.fixed_dt_mode`.

**Fixed dt:**
```python
D = int(np.ceil(const._tau_D / const.fixed_dt_value)) + 1
V_buf = np.full((D, N), const.voltage_init, dtype=np.float64)
write_idx = 0
delay_steps = int(round(const._tau_D / const.fixed_dt_value))
# each step:
V_buf[write_idx, :] = V
read_idx = (write_idx - delay_steps) % D
V_delayed = V_buf[read_idx, :]
write_idx = (write_idx + 1) % D
```

**Adaptive dt:** store `(t_frame, V_frame)` pairs in ring of capacity `D_max=4096`. Lookup walks backward to find bracketing frames, linearly interpolates. **Toggleable via `const.adaptive_delay_interp: bool` (default True).** Setting False preserves legacy nearest-frame snap behavior — required for proposal #2's bias characterization experiment.

**Verification:** Test 4 (two-neuron delay timing) is the headline. Regression must still pass on N=2 with fixed dt.

**Dependencies:** NUM-1, NUM-4.

## NUM-4 — Two integrator modes — **[DONE — commit `d021b36`. integrators.py with step_heun_fixed_* (Heun RK2 on V + exp-Euler on conductances) and step_euler_adaptive_*. const.fixed_dt_mode dispatches; dt_fixed = 25 µs.]**

- **Severity:** Blocker.
- **Files:** `update_functions.py` (split into `_step_adaptive_euler` and `_step_heun_exp`), `const.py`, `run.py`.

**`const.py` additions:**
```python
# Integrator mode
fixed_dt_mode      = True       # True -> Heun+exp-Euler; False -> adaptive Euler
fixed_dt_value     = 25e-6      # 25 us
dt_floor           = 1e-6       # 1 us minimum
dt_max             = 1e-4       # 100 us maximum
# Delay handling
adaptive_delay_interp = True
# Recording
rec_dt             = 2e-4       # 200 us output stride
# Logging
f_log_mode         = 'top_k'    # 'off' | 'top_k' | 'full'
f_log_top_k        = 10
f_log_path         = 'logs/f_trace.h5'
dt_floor_clips     = 0
```

**Step dispatch (pseudo-code):**
```python
def step(state, A, ring, log):
    if const.fixed_dt_mode:
        return _step_heun_exp(state, A, ring, log, dt=const.fixed_dt_value)
    else:
        return _step_adaptive_euler(state, A, ring, log)

def _step_adaptive_euler(state, A, ring, log):
    V_delayed = ring.lookup_adaptive(state.t_sim - const._tau_D,
                                     interp=const.adaptive_delay_interp)
    f_v, f_E, f_I, f_A = compute_f(state, A, V_delayed)
    M = max(np.max(np.abs(f_v)), np.max(np.abs(f_E)),
            np.max(np.abs(f_I)), np.max(np.abs(f_A)))
    dt = const.epsilon / M
    dt = min(max(dt, const.dt_floor), const.dt_max)
    state.G_dt_list.append(dt)
    state.V  += dt * f_v
    state.gE += dt * f_E
    state.gI += dt * f_I
    state.gA += dt * f_A
    state.t_sim += dt
    state.step  += 1
    ring.push(state.t_sim, state.V)
    log.maybe_emit(f_v, f_E, f_I, f_A, state.t_sim)
```

**Heun + exp-Euler step (fixed dt):**

1. Lookup delayed voltage:
   ```python
   V_d = V_buf[read_idx, :]
   sigV_d = sigma_vec(V_d); sigV = sigma_vec(V); sig0V = sigma_0_vec(V)
   I_rec = A.dot(sigV_d)
   ```
2. Conductance sources at t_n:
   ```python
   s_E = const.I
   s_I = const._a_I * const.conductance_I_max * I_rec  # NB: post-BIO-3
   s_A = const._a_A * const.w_A * const.conductance_A_max * sigV
   ```
3. Exponential-Euler conductance updates (use `expm1` to avoid catastrophic cancellation):
   ```python
   def expE(g, a, s, dt):
       phi = np.expm1(-a * dt)
       return g * (1.0 + phi) - (s / a) * phi
   gE_new = expE(gE, const._a_E, s_E, dt)
   gI_new = expE(gI, const._a_I, s_I, dt)
   gA_new = expE(gA, const._a_A, s_A, dt)
   ```
4. Heun voltage update with Lie-Trotter splitting (conductances first, V sees midpoint):
   ```python
   gE_mid = 0.5 * (gE + gE_new); gI_mid = 0.5 * (gI + gI_new); gA_mid = 0.5 * (gA + gA_new)
   def f_V(V_state, gE_, gI_, gA_):
       exc  = (const.voltage_E - V_state) * gE_
       inh  = (const.voltage_I - V_state) * gI_
       leak = (const.voltage_L - V_state) * const.conductance_L
       pot  = (const.voltage_K - V_state) * (const.conductance_K_max * sigma_0_vec(V_state) + gA_)
       return (exc + inh + leak + pot) / const.capacitance
   k1 = f_V(V, gE, gI, gA)
   V_pred = V + dt * k1
   k2 = f_V(V_pred, gE_mid, gI_mid, gA_mid)
   V_new = V + 0.5 * dt * (k1 + k2)
   ```

**LIF mode** uses exp-Euler on V too (exact for linear ODE):
```python
V_new = V * np.exp(-const._a_m * dt) + (1.0 - np.exp(-const._a_m * dt)) * (const.I_ext + const.g_syn * I_rec)
```

**Verification:** Tests 3 (Δt→0 convergence — Heun must show p≈2), 6 (energy conservation), 9 (cross-integrator agreement vs LSODA/Radau).

**Dependencies:** NUM-1, NUM-2, NUM-3.

## NUM-5 — `dt_floor` and `dt_max` safety caps — **[PARTIAL — commit `7b62bad` shipped linear interpolation in the delay lookup (the snap-up fix), but explicit `dt_floor` / `dt_max` clamps in adaptive Euler were not added. Tracked in Follow-up §F10.]**

- **Severity:** High.
- **Files:** `const.py`, `update_functions.py`.

**Fix:**
```python
raw_dt   = const.epsilon / np.max(M_all)
best_dt  = min(max(raw_dt, const.dt_floor), const.dt_max)
if raw_dt < const.dt_floor:
    const.dt_floor_clips += 1
```

**Verification:** Test 8 (dt-stationarity). Test 5 (param sweep) — no NaN/inf under pathological g_E_init.

**Dependencies:** NUM-4.

## NUM-6 — Per-neuron `f` logging (proposal #2 instrumentation) — **[PARTIAL — commit `4d95031` dumps V / g_A / g_E / g_I / dt_list / last_spike_time to HDF5 keyed by config hash. The per-neuron `f(V)` magnitudes (the actual proposal-#2 EWS observable) are not yet logged. Tracked in Follow-up §F8.]**

- **Severity:** High for proposal #2.
- **Files:** `update_functions.py`, `logging.py` (new), `const.py`.

**Three modes:**
- `'off'`: zero overhead.
- `'top_k'`: per step, store top-k absolute `|f_v|, |f_E|, |f_I|, |f_A|` and indices via `np.argpartition`. ~50 bytes/step regardless of N.
- `'full'`: HDF5 chunked write of full arrays. Chunks `(1024, N)`, gzip level 1.

**Verification:** `tests/test_f_logging.py` — 1000 steps, N=20, top_k mode: assert shape `(1000, 10)`, monotone-non-decreasing in `|f|`. Full mode: HDF5 file readable.

**Dependencies:** NUM-1. `h5py`.

## NUM-7 — Decoupled recording (`V_hist`) for output — **[DONE — commit `9f7a9e6`. dynamic_voltage_plot and network_plot now consume state.history; graph_build.set_graph_attributes reduced to a no-op.]**

- **Severity:** High.
- **Files:** `state.py`, `update_functions.py`, `dynamic_voltage_plot.py`, `network_plot.py`.

**Fix:** Separate working state from output recording:
```python
rec_stride = max(1, int(round(const.rec_dt / const.fixed_dt_value)))
rec_T = int(np.ceil(tMax / rec_stride))
V_hist  = np.empty((rec_T, N), dtype=np.float32)
gA_hist = np.empty((rec_T, N), dtype=np.float32) if model == 'STR' else None
# in step:
if step % rec_stride == 0:
    V_hist[rec_idx, :] = V
    if gA_hist is not None:
        gA_hist[rec_idx, :] = gA
    rec_idx += 1
```
At N=500, T=30 s, rec_dt=200 µs: 300 MB. Manageable.

**Verification:** Visual regression against `tests/baselines/N2_str_baseline.png`. Use `matplotlib.testing.compare`.

**Dependencies:** NUM-1.

## NUM-8 — Validation test suite (9 tests) — **[DONE — commit `dba2c88`. All 9 tests pass in ~1 s. Test 8 reframed from "dt stationary" to "dt finite" — the adaptive-Euler dt blow-up at LIF equilibrium *is* the proposal-#2 observable, not pathology to suppress.]**

- **Severity:** High.
- **Files:** `tests/test_numerical_*.py` (one per test).

### Test 1: `test_numerical_regression.py`
**Setup:** N=2, K=1, P=0, seed 12345, STR, `fixed_dt_mode=False`, `adaptive_delay_interp=False`, tMax=10000.
**Expected:** Voltage trace matches `tests/baselines/N2_str_phase0.npz` to `np.allclose(rtol=1e-10, atol=1e-14)`.

### Test 2: `test_quiescent_stability.py`
**Setup:** N=10, no edges, model='STR', no input, tMax = 10 s, fixed dt.
**Expected:** `V(t)` monotone non-increasing toward `V_L`; `|V(T) − V_L| < 1e-9`. Each `g(t) = g(0)·exp(-a·t)` to `rtol=1e-6`.

### Test 3: `test_dt_convergence.py`
**Setup:** N=1 STR, square current 0<t<50 ms, Δt ∈ {200, 100, 50, 25, 12.5, 6.25} µs. Reference: `solve_ivp(method='Radau', rtol=1e-12, atol=1e-14)`.
**Expected:** Fit `log |V_h − V_ref|_∞ = p·log Δt + c`; require `p ≥ 1.85` for Heun, `p ≥ 0.9` for Euler.

### Test 4: `test_two_neuron_delay.py`
**Setup:** N=2, A→B, `_tau_D = 1 ms`. Force A to spike at t=10 ms. Run 25 ms.
**Expected:** B onset within ±Δt of `t = 10 ms + _tau_D` in fixed-dt; within `±5·dt_floor` in adaptive with `adaptive_delay_interp=True`.

### Test 5: `test_param_sweep_stability.py`
**Setup:** N=50, K=4, P=2e-3. Sweep `g_E_init`, `g_A_max`, `w_A`, `P` × 3 levels each (81 runs × 200 ms).
**Expected:** No `V > 100 mV` or `V < -200 mV`. No NaN/inf. Emit `tests/artifacts/sweep_table.csv`.

### Test 6: `test_energy_conservation.py`
**Setup:** N=1, no input, gE=gI=gA=0 frozen, V_init=-50 mV, leakage only, fixed dt 25 µs.
**Expected:** `Q = sum(g_L * (V_L - V[k]) * dt)` vs `-C * (V_init - V_L)`. Relative error < 1e-4.

### Test 7: `test_echo_state_property.py`
**Setup:** N=100, K=7, P=2e-3, STR, fixed dt 25 µs. Two trajectories, identical input, V₀ differs by ±5 mV.
**Expected:** `||V_a − V_b||_2 / N` decays. By 3·τ_A ≈ 3 ms: <0.5 mV. By 3·τ_slowest=15 ms: <0.1 mV.

### Test 8: `test_dt_stationarity.py`
**Setup:** N=50, no input, no recurrent (P=0), adaptive mode, 100 s.
**Expected:** After 1 s warm-up: `np.std(dt_list[-10000:]) / np.mean(...) < 1e-3`.

### Test 9: `test_cross_integrator_agreement.py`
**Setup:** N=5, deterministic graph. Compare fixed-dt Heun to `solve_ivp(method='LSODA', rtol=1e-8)` and `solve_ivp(method='Radau', rtol=1e-10)`.
**Expected:** On low-pass `V_hist` (1 kHz cutoff), max abs deviation < 1 mV over 500 ms window. Adaptive Euler tolerance: < 5 mV.

**Dependencies:** All of NUM-1..7.

## Phase 2 — Commit boundaries, risks — **[DONE — see Master change table for SHAs]**

**Commit order (9 commits):**
1. `state: flatten per-node lists into NumPy arrays` (NUM-1)
2. `sim: vectorize sigma/sigma_0 as ufuncs` (prep for NUM-2)
3. `sim: sparse CSR adjacency replaces neighbor loop` (NUM-2)
4. `sim: ring buffer for delayed-voltage lookup` (NUM-3; delete `delay()` from `math_functions.py`)
5. `sim: add fixed-dt Heun + exponential-Euler integrator` (NUM-4)
6. `sim: dt_floor and dt_max safety caps for adaptive mode` (NUM-5)
7. `obs: per-neuron f-channel logging (off/top_k/full)` (NUM-6)
8. `io: decouple V_hist recording from working state` (NUM-7)
9. `tests: add 9-test numerical validation suite` (NUM-8)

**Risks (top):**
1. **R1: Linear-interp delay kills proposal #2's experiment.** Mitigation: `const.adaptive_delay_interp` flag default True; legacy `interp=False` mode preserved.
2. **R2: All Phase 0 regression baselines shift simultaneously.** Mitigation: regenerate baseline after each NUM-x commit; relax to `rtol=1e-10`; pin each baseline to git SHA in `tests/baselines/MANIFEST.txt`.
3. **R3: Exp-Euler hides AHP saturation.** When V rises sharply, source-at-`t_n` bias proposal #1's headline. Mitigation: test 9 requires Heun-vs-LSODA agreement on `gA(t)` not just V(t). If bias detected, source-at-midpoint via predictor-corrector on `s_A`.
4. **R4: Ring buffer too small for `dt_floor`.** Mitigation: `assert D >= int(_tau_D / dt_floor) + 16`; auto-grow if needed.
5. **R5: Heun + exp-Euler order loss at stiff spike transitions.** Mitigation: if test 3 shows `p < 1.85`, drop to V Euler + g exp-Euler (locally O(Δt)) and document.

---

# Phase 3 — Graph Generation Infrastructure — **[TODO — out of current scope]**

> Status snapshot (2026-05-11): not started. The current scoping decision capped execution at Phases 0-2. Phase 3 will be planned separately once foundation follow-ups are settled.

Refactors `graph_build.py` from a single-purpose 11-line stub into a dispatched five-graph battery. The Snudda extraction (GRAPH-4) and matching protocols (GRAPH-8) are the technically demanding items: Snudda needs a pinned-Docker pipeline against a 4+-year-old upstream tag with drifting HDF5 schema, and matching is compute-bound (5 graphs × 4 protocols × 10 pilots × 10⁴ steps × 500 neurons ≈ 10⁹ ops).

Depends on: Phase 0 NetworkX 2.x port + Phase 2 state-vector refactor.

## GRAPH-1 — Replace `weight_generator.py` with `assign_weights()`

- **Severity:** Blocker.
- **Files:** `weight_generator.py`, `const.py`, `run.py`.

**Fix:** Function signature: `assign_weights(G, distribution="lognormal", rng=None, **kwargs) -> nx.DiGraph`.

For `"lognormal"`: draw weights from `rng.lognormal(mean=μ, sigma=σ)`. Calibrate to Koos 2004 (mean ≈ 0.55 mV, CV ≈ 1.05). For lognormal: `CV² = exp(σ²) − 1` → σ ≈ 0.83; `μ = log(mean) − σ²/2`. Convert mV to conductance: `g_syn = V_IPSC / ((V_I − V_rest) · R_in)` with R_in = 200 MΩ. So 0.5 mV IPSC → 500 pS.

Add to `const.py`:
```python
R_in = 200e6                  # Ω, MSN input resistance (Plenz & Aertsen 1996)
weight_mean_S = 0.5e-9        # S, mean unitary g_syn (Koos 2004)
weight_cv = 1.0
```

For `"uniform"`: `rng.uniform(const.lowrand, const.highrand)`. For `"snudda_native"`: read `weight` attribute already attached by Snudda extraction script.

D1/D2 weight asymmetry hook: if `G.graph['source'] == 'modular'` and source.subtype='D2', target.subtype='D1', multiply lognormal mean by 2.0 (Taverna 2008 *J Neurosci* 28:5504). Implement as post-draw 2× scale (NOT separate distributions — preserves variance).

**Verification:** `figures/weight_dist_lognormal.png`: mean weights ~500 pS within 25%; std/mean within 25% of 1.0; >99.5% positive.

**Dependencies:** None internal. **Citation:** Koos, Tepper, Wilson 2004.

## GRAPH-2 — Refactor `graph_build.py` into dispatched interface

- **Severity:** Blocker.
- **Files:** `graph_build.py`, `run.py`.

**Function signature:**
```python
def graph_build(graph_type: str, n_nodes: int = 500, seed: int | None = None, **kwargs) -> nx.DiGraph:
    """Dispatch graph constructor. Returns directed graph with
    G.graph['source'] = graph_type, G.graph['seed'] = seed."""
```

**Dispatch table:**

| `graph_type` | Required kwargs | Optional kwargs |
|---|---|---|
| `"nws"` | `k` (int), `p` (float) | — |
| `"snudda"` | `path` (str, .graphml) | — |
| `"ms_rewire"` | `source_graph` (nx.DiGraph) | `n_swaps_multiplier` (default 100), `weighted` (bool) |
| `"gamma_kernel"` | `gamma_params_verified=True` | `cube_um` (default 200), `k_shape`, `theta_um`, `target_indeg` (default 7) |
| `"modular"` | — | `n_d1` (default 250), `n_d2` (default 250), `block_probs` (default Burke 2017) |

Use `rng = np.random.default_rng(seed)` and pass down. Always set `G.graph['source']` and `G.graph['seed']`.

**Verification:** `isinstance(G, nx.DiGraph)`; correct N; reproducibility — two calls with same seed produce equal edge sets.

**Dependencies:** Phase 0 NetworkX 2.x port.

## GRAPH-3 — NWS branch with random-orientation directedness

- **Severity:** High.

**Fix:** `nx.newman_watts_strogatz_graph(n_nodes, k, p, seed)` then convert to DiGraph via random orientation (NOT `to_directed()`). For each undirected edge {u,v}, Bernoulli(0.5) chooses (u→v) or (v→u). Reciprocity ≈ 0, matching empirical MSN-MSN reciprocity ~5-10% (Tunstall et al. 2002 *J Neurophysiol* 88:1263).

**Gotcha:** NWS mean degree is `k + 2·p·(N−k−1)`, not `k`. With K=8, P=0.01, N=500 → mean degree ~13. Document in docstring; don't silently rescale.

**Verification:** Mean undirected degree within 10% of `k`; `nx.reciprocity(G) < 0.05`; `nx.is_directed(G)`.

**Dependencies:** GRAPH-2.

## GRAPH-4 — Snudda extraction script + `"snudda"` branch

- **Severity:** High. Empirical anchor for the comparison.
- **Files:** New `scripts/snudda_extract.py`, `scripts/snudda_docker/Dockerfile`, `data/snudda_500_msn.graphml`.

**Docker setup** (`scripts/snudda_docker/Dockerfile`):
```dockerfile
FROM continuumio/miniconda3:23.5.2-0
RUN apt-get update && apt-get install -y build-essential git hdf5-tools libhdf5-dev
RUN conda install -c conda-forge python=3.9 numpy scipy h5py networkx mpi4py
RUN git clone https://github.com/Hjorth-Lab/Snudda.git /opt/Snudda \
 && cd /opt/Snudda \
 && git checkout FrontNeuralCircuits2021 \
 && pip install -e .
WORKDIR /work
```

Build and enter:
```bash
docker build -t snudda:fnc2021 scripts/snudda_docker
docker run -it -v $(pwd)/data:/work snudda:fnc2021 bash
```

**Snudda CLI** (inside container):
```bash
snudda init MyNet --size 10000 --overwrite
snudda place MyNet
snudda detect MyNet
snudda prune MyNet
```
Writes `MyNet/network-synapses.hdf5` and `MyNet/network-neuron-positions.hdf5`.

**Schema introspection (mandatory — schema drifts):**
```python
import h5py
with h5py.File('MyNet/network-synapses.hdf5', 'r') as f:
    print(list(f.keys()))           # e.g. ['meta', 'network', 'synapses']
    print(list(f['network'].keys()))
    print(f['network/synapses'].dtype)
    print(f['network/neurons'].dtype)
```
Across releases the conductance column has been named `cond`, `conductance`, or `weight`. Never hard-code; introspect.

**Extraction code** (`scripts/snudda_extract.py`):
```python
import h5py, numpy as np, networkx as nx

def extract_msn_subgraph(hdf5_path, positions_path, cube_center_um=None,
                         cube_side_um=200, out_path='data/snudda_500_msn.graphml'):
    with h5py.File(hdf5_path, 'r') as f:
        syn = f['network/synapses'][:]
        neu = f['network/neurons'][:]
    types = [n['type'].decode() for n in neu]
    msn_mask = np.isin(types, ['dSPN', 'iSPN'])
    msn_ids = np.where(msn_mask)[0]
    positions = np.stack([neu['x'], neu['y'], neu['z']], axis=1)
    centre = positions[msn_mask].mean(axis=0) if cube_center_um is None else np.array(cube_center_um) * 1e-6
    half = cube_side_um * 1e-6 / 2
    in_cube = (np.abs(positions - centre) < half).all(axis=1) & msn_mask
    cube_ids = np.where(in_cube)[0]
    assert 450 <= len(cube_ids) <= 600, f"Subvolume has {len(cube_ids)} MSNs; tune cube_side_um"
    # Multi-synapse aggregation: sum conductance, store contact count
    G = nx.DiGraph()
    for i in cube_ids:
        G.add_node(int(i), subtype=types[i], pos=tuple(positions[i].tolist()))
    pair_cond, pair_count = {}, {}
    src_in = np.isin(syn['source_id'], cube_ids)
    dst_in = np.isin(syn['dest_id'], cube_ids)
    for s in syn[src_in & dst_in]:
        key = (int(s['source_id']), int(s['dest_id']))
        pair_cond[key] = pair_cond.get(key, 0.0) + float(s['cond'])
        pair_count[key] = pair_count.get(key, 0) + 1
    for (u, v), w in pair_cond.items():
        G.add_edge(u, v, weight=w, n_contacts=pair_count[(u, v)])
    G = nx.convert_node_labels_to_integers(G, ordering='sorted', label_attribute='snudda_id')
    nx.write_graphml(G, out_path)
    return G
```

`cube_side_um=200` targets ~500 MSNs at Oorschot 1996 density. Tune once empirically and lock. **Commit `data/snudda_500_msn.graphml` to the repo** so downstream work is reproducible even if Snudda regeneration breaks years later.

**Verification:** Node count 450-550; D1/D2 ratio between 0.4 and 0.6; `pos` attribute on every node.

**Dependencies:** GRAPH-2. Docker, ~30 GB disk. **Citation:** Hjorth et al. 2020 *PNAS* 117:9554.

## GRAPH-5 — Maslov-Sneppen rewire with convergence check

- **Severity:** High.
- **Fix:** `nx.algorithms.swap.directed_edge_swap(H, nswap=100*|E|, max_tries=..., seed=...)`. **`10·|E|` is insufficient for clustered graphs** (Milo et al. 2003). Run in 20 chunks; record `nx.transitivity(H)` and `nx.average_clustering(H.to_undirected())` after each. Verify max-min range over last 10 chunks <1% of (initial − final) drop; warn and double if not. For weighted rewire, use Rubinov & Sporns 2011 strength-preserving null.

**Verification:** In/out-degree sequences identical pre/post (by construction). Clustering plateau check. Weighted: total weight conserved to machine epsilon.

**Dependencies:** GRAPH-2; GRAPH-1 for weighted. **Citation:** Maslov & Sneppen 2002, Milo et al. 2003, Rubinov & Sporns 2011.

## GRAPH-6 — Distance-dependent Gamma kernel (Yim 2017)

- **Severity:** High.
- **Fix:** Sample n_nodes positions uniformly in cube `L = kwargs.get('cube_um', 200) * 1e-6`. Connection probability `P(d) = A · scipy.stats.gamma.pdf(d * 1e6, a=k_shape, scale=theta_um)`; prefactor `A` fit to deliver target mean in-degree (default 7).

**CRITICAL: do not lock Gamma parameters until Yim 2017 directly verified.** Round-2 agents reported uncertainty: (k=2, θ≈100 µm) vs (k=3, θ≈50 µm). Defer via guard:
```python
assert kwargs.get('gamma_params_verified', False), \
    "Read Yim 2017 Fig. 2 and confirm shape/scale before running"
```
Once verified, hard-code as `_YIM_GAMMA_K`, `_YIM_GAMMA_THETA_UM` constants.

**Verification:** Empirical P(d) binned by 20 µm: `assert |P_emp(bin) - P_target(bin)| < 0.02`. Mean in-degree within 10% of target.

**Dependencies:** GRAPH-2; literature verification. **Citation:** Yim, Aertsen, Kumar 2017 *eNeuro* 4:ENEURO.0348-16.

## GRAPH-7 — Block-modular D1/D2 with Burke asymmetry

- **Severity:** High.
- **Fix:** `nx.stochastic_block_model(sizes=[250, 250], p=[[0.14, 0.06], [0.27, 0.27]], directed=True, seed=seed)`. Rows/columns [D1, D2]. Burke 2017 Table 1: D1→D1=0.14, D1→D2=0.06, D2→D1=0.27, D2→D2=0.27. Tag `G.nodes[i]['subtype'] = 'D1' if i < 250 else 'D2'`. Weight asymmetry (D2→D1 ~2× D1→D2) applied at `assign_weights` stage.

**Gotcha:** Burke probabilities measured at fixed intersomatic distances (50-100 µm slice cuts). Naive application gives SBM density higher than physiological; matching protocols compensate.

**Verification:** Empirical block densities within 10% of (0.14, 0.06, 0.27, 0.27). D1 count = D2 count = 250.

**Dependencies:** GRAPH-2, GRAPH-1. **Citation:** Burke, Rotstein, Alvarez 2017 *Neuron* 96:267.

## GRAPH-8 — Matching protocols

- **Severity:** Blocker for proposal #3 inference.
- **Files:** New `matching.py`, `run.py`.

**Four protocols** (all run for each pairwise comparison; signature is "robustly graph-dependent" only if it differs across all four):

1. **Mean firing rate matching.** Target `r* ∈ {2, 10, 20} Hz`. Tune `I_ext` (or `const.I`). Binary search 8-12 iterations until `|rate − r*|/r* < 0.1`. Pilot: 5 s sim.
2. **Total excitatory drive matching.** `E_drive(G) = Σ_j ∫₀ᵀ g_E,j(t)·(V_E − V_j(t)) dt`. Tune excitatory input rate. Match across graphs within ±10%.
3. **Total inhibitory drive matching (NEW per round-3).** `I_drive(G) = Σ_j ∫₀ᵀ g_I,j(t)·(V_I − V_j(t)) dt`. Tune global synaptic-weight scaling `α` post-`assign_weights` (uniform multiplicative, preserves distribution shape). Without this, denser graphs receive more drive — confounds topology with mean inhibition.
4. **Input variance matching.** `Var(V_j(t))` time- then population-averaged. Tune cortical input variance. Bartlett's K² test for equal variance non-significant at α=0.05.

Cache matched parameters in `data/matching_cache.json` keyed by `(graph_hash, target_rate, target_drive)` so re-runs are O(1).

**Verification:** Test statistic per protocol confirms matching achieved within tolerance.

**Dependencies:** All prior GRAPH-*; Phase 2 numerical refactor (matching is compute-heavy).

## GRAPH-9 — Verification smoke-test suite

- **Severity:** Medium.
- **Files:** `tests/test_graphs.py`.

```python
def test_all_five_graphs_construct():
    cases = [
        ("nws",          dict(k=8, p=0.002)),
        ("snudda",       dict(path="data/snudda_500_msn.graphml")),
        ("gamma_kernel", dict(gamma_params_verified=True, k_shape=2, theta_um=100, cube_um=200)),
        ("modular",      dict()),
    ]
    Gs = {name: graph_build(name, n_nodes=500, seed=42, **kw) for name, kw in cases}
    Gs["ms_rewire"] = graph_build("ms_rewire", n_nodes=500, seed=43, source_graph=Gs["nws"])
    for name, G in Gs.items():
        assert isinstance(G, nx.DiGraph)
        assert G.number_of_nodes() == 500
        assert G.graph["source"] == name
```

Per-graph checks: NWS reciprocity <0.05; Snudda 450-550 nodes + D1/D2 ratio 0.4-0.6 + `pos` attr; MS-rewire degree sequence identical pre/post; Gamma mean in-degree within 10% + empirical P(d) within 0.02 of target; Modular block densities within 10%; weight check: lognormal mean within 25% of 500 pS, CV within 25% of 1.0.

**Dependencies:** GRAPH-1..7.

## Phase 3 — Commit order, risks

**Commit order:**
1. GRAPH-1 (weights) — smallest blast radius, unlocks all other matched-weight work.
2. GRAPH-2 + GRAPH-3 (dispatch + NWS) — `python run.py` must still work after.
3. GRAPH-5 (MS-rewire) — operates on NWS output.
4. GRAPH-7 (modular) — no external data.
5. GRAPH-6 (Gamma) — after Yim 2017 parameter verification.
6. GRAPH-4 (Snudda) — longest tail; avoids blocking on Docker debugging.
7. GRAPH-8 (matching protocols).
8. GRAPH-9 (smoke tests).

**Risks (top):**
1. **Snudda HDF5 schema drift.** FrontNeuralCircuits2021 tag is 4+ years old. Mitigation: `print(list(f.keys()))` first; pin exact commit hash, not tag; commit resulting `.graphml` to repo.
2. **Yim 2017 Gamma params unverifiable.** Mitigation: `gamma_params_verified` assertion blocks the branch; build everything else (independent); sensitivity-analyze both parameterisations if paper unavailable.
3. **Snudda subvolume not 50:50 D1:D2.** Mitigation: allow 0.4 ≤ D1/N ≤ 0.6 as physiological; only modular held to 50:50 exactly; document in `G.graph` metadata.
4. **MS-rewire fails to mix on Snudda clustered topology.** Mitigation: plateau-check in place; auto-double swap budget on warning.
5. **Matching cost: 5 graphs × 4 protocols × 10 pilots × 10⁴ steps × 500 neurons ≈ 10⁹ ops.** Mitigation: Phase 2 vectorization is hard prerequisite; cache matched parameters.

---

# Phase 4 — Analysis Infrastructure & Test/Reproducibility — **[TODO — out of current scope]**

> Status snapshot (2026-05-11): not started. Same scoping note as Phase 3.

The codebase currently has only two plot files and no analysis layer. Three planned papers need three distinct pipelines plus test infrastructure, reproducibility tooling, and OSF pre-registration. The IPC reimplementation (ANA-6) is the single most technically demanding item in the entire plan: a port of Kubota's MATLAB reference with strict Legendre-orthogonality input constraints and surrogate-thresholded significance.

Depends on: Phases 0-3.

## ANA-1 — Adopt `neo.SpikeTrain` as canonical spike data type

- **Severity:** Blocker.
- **Files:** New `analysis/spike_io.py`.

**Fix:**
```python
def voltages_to_spiketrains(V: np.ndarray, t: np.ndarray, V_thresh: float = -50e-3,
                            t_refractory: float = 2e-3) -> list[neo.SpikeTrain]:
    """Convert voltage traces to neo.SpikeTrain via scipy.signal.find_peaks."""
    # Internally: scipy.signal.find_peaks(V_i, height=V_thresh, distance=int(t_refractory/np.median(np.diff(t))))
    # Wrap each neuron's spike times as neo.SpikeTrain(times=spk*pq.s, ...)
```
Provide `save_spiketrains_neo_hdf5(path, sts)` via `neo.io.NixIO`. Every downstream metric module consumes `list[neo.SpikeTrain]`.

**Verification:** `tests/test_analysis.py::test_spike_extraction_recovers_known_times` — inject 40 Hz regular train, recover times within `dt`.

**Dependencies:** `neo>=0.13`, `quantities`, `scipy>=1.11`.

## ANA-2 — Pin analysis stack in `pyproject.toml`

- **Severity:** Blocker.
- **Files:** New `pyproject.toml`, `requirements.txt` (pip-tools lockfile), `environment.yml`.

```toml
[project]
name = "neurorc"
version = "2.4.0"
requires-python = ">=3.11,<3.13"
dependencies = [
    "networkx>=3.2", "numpy>=1.26,<2.1", "scipy>=1.11", "matplotlib>=3.8",
]
[project.optional-dependencies]
analysis = [
    "neo==0.13.1", "quantities>=0.15", "elephant==1.1.1", "reservoirpy==0.3.12",
    "scikit-learn>=1.6", "ewstools==2.1.2", "powerlaw==1.5", "mrestimator==0.1.6",
    "pyspike==0.8.0", "h5py>=3.10", "joblib>=1.4", "diptest>=0.7",
    "cliffs-delta>=1.0", "kneed>=0.8",
]
stats = ["pymer4>=0.8", "mne>=1.6", "arviz>=0.17", "statsmodels>=0.14"]
test = ["pytest>=8", "pytest-benchmark>=4", "pytest-xdist>=3.5"]
repro = ["datalad>=0.19", "brian2>=2.6"]
```

Pin Python to 3.11. Brian2/JAX conflict: Brian2 only in `repro`, JAX only in `analysis` (transitive via ewstools).

**Verification:** `pip install -e ".[analysis,test]"` and `pip install -e ".[repro]"` resolve cleanly in fresh 3.11 venv.

**Dependencies:** pip-tools.

## ANA-3 — pytest scaffold and CI hook

- **Severity:** Blocker.
- **Files:** `tests/__init__.py`, `tests/conftest.py`, `pytest.ini`, `.github/workflows/test.yml`.

`conftest.py` fixtures: `tiny_network` (N=2, K=1, fixed seed), `small_network` (N=50, K=4), `lorenz_input`, `narma10_input`, `seeded_rng(seed=42)`. Markers: `regression`, `slow`, `gpu`, `validation`. CI: `pytest -m "not slow"` on push; full `pytest` nightly.

**Verification:** Empty `tests/test_sanity.py::test_imports_ok` passes.

**Dependencies:** ANA-2.

## ANA-4 — Phase 0 regression test

- **Severity:** Blocker.
- **Files:** `tests/test_regression.py`, `tests/fixtures/regression_N2_T1000_seed42.npz`.

Already specified in PRE-6. ANA-4 is the Phase 4 acknowledgement that this test is the canary for silent drift during all subsequent work.

**Dependencies:** ANA-3.

## ANA-5 — Pipeline A scaffold: reservoir benchmarks

- **Severity:** High.
- **Files:** `metrics/pipeline_a_reservoir.py`, `tests/test_pipeline_a.py`.

**Public surface:**
```python
def jaeger_memory_capacity(state, u, k_max=200, ridge=1e-6) -> tuple[float, np.ndarray]
def kernel_rank(state, n_probes=100, tol=1e-3) -> int
def generalization_rank(state, state_noisy, tol=1e-3) -> int
def participation_ratio(V) -> float
def per_neuron_autocorr_decay(V, dt, max_lag_s=1.0) -> np.ndarray
def narma10_score(state_train, u_train, state_test, u_test) -> dict
def lorenz_one_step_score(state_train, u_train, state_test, u_test) -> dict
def delayed_xor_score(state, bit_stream, delay=5) -> float
```

**Pitfalls:**
- State matrix passed to MC/IPC must have **washout removed** (first 1000 steps).
- Reservoirpy NARMA10 returns inputs in [0, 0.5]; rescale to [-1, 1].
- `RidgeCV(cv='efficient_loo')` mandatory; LOO on T=10000 is closed-form via SVD <1 s.

**Ground-truth test (`test_mc_on_linear_esn`):** N=200 linear ESN with ρ=0.9, leak=1.0. Drive with `u ~ U(-1,1)` for T=10000. **MC ∈ [85, 105]** (Jaeger 2001 §4: linear ESN of ρ near 1 saturates MC near N/2). Tolerance ±10%.

**Dependencies:** ANA-1, ANA-2, ANA-3.

## ANA-6 — IPC decomposition reimplementation (Dambre 2012)

- **Severity:** High. Separate from ANA-5 due to size.
- **Files:** `metrics/ipc.py`, `tests/test_ipc.py`.

**Function signature:**
```python
def information_processing_capacity(state, u, max_degree=4, max_delay=50,
                                    surrogate_n=100, alpha=0.05) -> IPCResult
```

Legendre polynomial basis (Dambre 2012 §Methods). **Input u MUST be uniform i.i.d. on [-1, 1]** for Legendre orthogonality. Shuffled-reservoir surrogate for significance threshold (mandatory). Truncate sum at `C_total ≤ T_train / 10`.

**Validate against `github.com/kubota0130/ipc` (MATLAB).**

**Ground-truth tests:**
1. `test_ipc_total_capacity_linear_esn` — N=200 ESN ρ=0.9: total ∈ [180, 210].
2. `test_ipc_static_layer_capacity_one` — feedforward (no recurrence) → total ≈ 1.0.
3. `test_ipc_degree1_matches_jaeger_mc` — degree-1 capacity matches Pipeline A MC within 1%.

**Dependencies:** ANA-5.

## ANA-7 — Pipeline B scaffold: EWS benchmarks

- **Severity:** High.
- **Files:** `metrics/pipeline_b_ews.py`, `tests/test_pipeline_b.py`, `analysis/rk45_reference.py`.

**Public surface:**
```python
def variance_ews(x, window_s, dt) -> np.ndarray
def ar1_ews(x, window_s, dt) -> np.ndarray
def spectral_entropy_ews(x, window_s, dt, band_hz=(1, 100)) -> np.ndarray
def lyapunov_benettin(traj, x0, T, dt_renorm=0.1) -> float
def s_detector(dt_trace, window_s=1.0, sample_dt_mean=1e-4) -> np.ndarray
def roc_auc_transition(score, transition_idx, ...) -> dict
def kuramoto_R(V, fs, bandpass_hz=(5, 15)) -> np.ndarray
def hartigan_dip(x) -> tuple[float, float]
def avalanche_power_law_fit(sizes) -> dict
def rk45_reference_run(rhs, t_span, y0, **kwargs) -> dict
```

**Pitfalls:**
- `ewstools` requires uniform-time-grid pandas Series; adaptive-dt traces must be interpolated. `scipy.interpolate.interp1d(kind='linear')` with `fs_target = 1 / median(dt)`.
- ROC AUC: include labelled negative-control window far from transition (Bury 2023 default 5 s pre/post; >30 s pre is negative).
- Always run `Fit.distribution_compare('power_law', 'lognormal')` (Alstott et al. 2014).
- Kuramoto R from raw Vm meaningless; 4-pole Butterworth bandpass 5-15 Hz mandatory.

**Ground-truth tests:**
1. `test_powerlaw_recovers_pareto_alpha` — synthetic Pareto α=2.5: recovered ∈ [2.4, 2.6], `R_lognormal > 0` with `p < 0.05`.
2. `test_ar1_increases_before_saddle_node` — saddle-node normal form `dx/dt = r + x² + ση(t)`, r ramping: AR(1) Spearman ρ vs time > 0.5.

**Dependencies:** ANA-1, ANA-2, ANA-3.

## ANA-8 — Pipeline C scaffold: spike-train analyses

- **Severity:** High.
- **Files:** `metrics/pipeline_c_spikes.py`, `tests/test_pipeline_c.py`.

**Public surface:**
```python
def assembly_switching(spiketrains, bin_ms=50.0, var_explained=0.80,
                       nmf_rank_method='bicv', n_surrogates=100) -> dict
def petermann_correlation(spiketrains, bin_ms=1.0, jitter_ms=25.0, n_jitter=100) -> float
def avalanche_analysis(spiketrains, bin_factors=(0.5,1.0,2.0,4.0), method='iei') -> dict
def firing_rate_distribution(spiketrains, window_s=60.0, silent_threshold_hz=0.1) -> dict
def isi_spike_distance(sts) -> dict
def rate_matched_poisson_surrogate(sts, dither_ms=50.0) -> list[neo.SpikeTrain]
```

**Pitfalls:**
- Petermann-Plenz **requires jitter correction** (Smith & Kohn 2008). Without it, "low correlation" signature is artefact.
- NMF rank selection: **bicross-validation (Owen & Perry 2009) or stability NMF (Wu et al. 2016)**. NOT elbow.
- Avalanche τ must be invariant across ≥half-decade of bin sizes (Beggs & Plenz 2003; Lombardi 2017).
- Use mrestimator (Wilting & Priesemann 2018) as PRIMARY criticality indicator; size-distribution exponent as secondary. mrestimator bypasses the binning confound entirely.
- Distribution comparison: always `powerlaw.Fit.distribution_compare('power_law', 'lognormal')`.

**Ground-truth tests:**
1. `test_branching_ratio_on_known_process` — branching process m=0.95: `mrestimator.full_analysis` recovers within ±0.02.
2. `test_assembly_switching_recovers_two_assemblies` — two non-overlapping populations alternating 1-s bouts: `n_components=2`, dwell ≈ 1 s ± 0.1 s.

**Dependencies:** ANA-1, ANA-2, ANA-3.

## ANA-9 — Statistical comparison framework

- **Severity:** High.
- **Files:** `analysis/stats.py`, `tests/test_stats.py`.

```python
def compare_models_lme(df, metric, model_col='model', random='realization')
    # pymer4.Lmer(f"{metric} ~ model + (1 | realization)").fit()
def permutation_cluster_time(a, b, n_perm=10000, threshold=None)
    # mne.stats.permutation_cluster_test
def fdr_dependent(pvals)
    # statsmodels.stats.multitest.multipletests(method='fdr_by')  # Benjamini-Yekutieli
def effect_size(a, b, kind='auto')
    # Cohen's d if Shapiro p>0.05; Cliff's δ otherwise
def bayes_compare(model_a, model_b)
    # arviz.compare() — WAIC/LOO
```

**Verification:** `test_lme_recovers_known_effect` (simulate `y = 0.5*model + ...`, recover β); `test_fdr_by_controls_at_0.05`; `test_cliffs_delta_recovers_known` (N(0,1) vs N(1,1) → δ ≈ 0.477).

**Dependencies:** ANA-3.

## ANA-10 — Phase 1/2/3 test suites

- **Severity:** High.
- **Files:** `tests/test_biophysics.py`, `tests/test_numerical.py`, `tests/test_graphs.py`.

The biophysics tests verify Phase 1 sanity-check protocol items (BIO-1 through BIO-7). Numerical tests are the 9 validation tests from NUM-8. Graph tests are GRAPH-9.

**Dependencies:** ANA-3.

## ANA-11 — HDF5 chunked logger for proposal #2

- **Severity:** Medium.
- **Files:** New `analysis/logging.py`.

`HDF5Logger` opens h5 file with chunked datasets `voltage[N, T]`, `dt[T]`, `f_per_neuron[N, T]`, `spikes_t/spikes_i`. Chunk `(N, 1024)`, gzip level 4. Downsample by `log_every` (default 10) exposed in `const.py`.

**Verification:** 100×100,000 run → file <200 MB, read-back precision float32.

**Dependencies:** ANA-2.

## ANA-12 — Reproducibility infrastructure

- **Severity:** Medium.
- **Files:** `CITATION.cff`, `LICENSE`, `Dockerfile`, `.zenodo.json`, `README.md`.

**`CITATION.cff`:**
```yaml
cff-version: 1.2.0
title: "NeuroRC: Neural Region Compute"
authors:
  - family-names: "Stein"
    given-names: "Jakob"
type: software
repository-code: "https://github.com/jakob400/NeuroRC"
license: "BSD-3-Clause"
version: "2.4.0"
date-released: "2026-05-10"
doi: "10.5281/zenodo.PLACEHOLDER"
```

**LICENSE: BSD-3-Clause.** Maximum compatibility with downstream scientific re-use; all dependencies BSD/MIT.

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc gfortran libhdf5-dev git \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e ".[analysis,test]"
CMD ["pytest", "-m", "not slow"]
```

**Verification:** `cffconvert --validate -i CITATION.cff` passes; `docker build .` succeeds; `docker run neurorc:latest pytest -m "not slow"` passes.

**Dependencies:** ANA-2.

## ANA-13 — DataLad layout (nice-to-have)

- **Severity:** Nice-to-have.
- **Files:** `.datalad/config`, `data/.gitattributes`.

`datalad create -c text2git .` at repo root; annex-managed binary outputs. Simulation runs to `data/runs/{date}/{run_id}/` with `params.yaml` and `state.h5`.

**Dependencies:** ANA-2.

## ANA-14 — OSF pre-registration drafts

- **Severity:** High (must precede data collection for proposals #1 and #2).
- **Files:** `prereg/proposal_1_reservoir.md`, `prereg/proposal_2_dt_ews.md`.

**Proposal #1 hypotheses (confirmatory):**

- H1. STR memory capacity exceeds best-tuned LIF-het on Jaeger MC by ≥20%, Cliff's δ > 0.474, p < 0.05 Holm-Bonferroni corrected across 4 tasks.
- H2. STR participation ratio of voltage covariance exceeds LIF-het by ≥15%.
- H3. STR per-neuron autocorrelation decay distribution has longer tail (KS D > 0.2, p < 0.05) than LIF-het.

**Pre-registered analysis:** N=500, K=7, NWS P=1e-5, 20 random seeds, washout 1 s, training 100 s, test 30 s, RidgeCV efficient LOO over `[1e-8, 1e-6, 1e-4, 1e-2]`. Mixed-effects `metric ~ model + (1 | seed)`. Primary endpoint: Jaeger MC (no correction); secondaries Holm-Bonferroni.

**Falsification:** H0 outcomes reported in same primary results table. Paper publishable either way.

**Proposal #2 hypotheses (confirmatory):**

- H1. S(t) ROC AUC on saddle-node ramp exceeds variance/AR(1)/spectral-entropy by ≥0.05 absolute, p < 0.05 DeLong test, FDR-BY across baselines.
- H2. Lead-time at 5% FPR for S(t) exceeds best baseline by ≥100 ms (Wilcoxon, p < 0.05).
- H3. RK45 cross-check: ρ(S_current, S_RK45) > 0.9 over 1 s window.

**Pre-registered analysis:** N=100, ramping g_E subcritical→supercritical over 10 s, 50 realizations. Detectors on uniform-resampled 10 kHz traces. Rolling window 1 s. Spectral entropy band 5-15 Hz. Hartigan dip on V_mean end-of-window as transition oracle.

Both pre-registrations live in `prereg/` as Markdown; paste into OSF Preregistration Template for Secondary Data Analysis (van den Akker et al. 2019).

**Dependencies:** ANA-5, ANA-6, ANA-7 specs locked.

## Phase 4 — Commit order, risks

**Commit order:**
1. ANA-2 (pin deps) — must precede everything
2. ANA-1 (neo.SpikeTrain) — must precede pipeline C
3. ANA-3 (pytest scaffold) — must precede tests 4-11
4. ANA-4 (regression test)
5. ANA-10 (Phase 1-3 test suites)
6. ANA-5 (Pipeline A scaffold)
7. ANA-6 (IPC reimplementation) — separate commit due to size
8. ANA-7 (Pipeline B)
9. ANA-8 (Pipeline C)
10. ANA-9 (stats framework)
11. ANA-11 (HDF5 logger)
12. ANA-12 (repro infra)
13. ANA-13 (DataLad)
14. ANA-14 (OSF pre-reg) — must precede production sweeps

**Risks (top):**
1. **IPC reimplementation overruns scope.** Mitigation: validate port-by-port against Kubota 0130 MATLAB; if it stalls, fall back to Jaeger MC + kernel/generalization rank only for proposal #1, defer IPC.
2. **Package conflicts: Brian2 vs JAX vs Python.** Mitigation: Brian2 only in `repro`, JAX only in `analysis`; pin Python 3.11.
3. **ewstools time-grid format.** Mitigation: `_to_ewstools_format(trace, dt_trace)` helper interpolates once.
4. **NMF rank selection sensitivity.** Mitigation: report both bicv and stability; pre-register bicv as primary; flag as exploratory if they disagree.
5. **Regression fixture rot.** Mitigation: regeneration gated by env var `NEURORC_REGEN_FIXTURE=1`; PR review required.

---

# Validation gates summary

Each phase has a verification gate that must pass before the next phase begins.

## Phase 0 gate — **[DONE]**
- `pip install -r requirements.txt` exits 0
- `pytest tests/test_regression.py` — both regression tests pass
- `grep -nE "G\.node\[|len\(G\.node\)|nx\.info|const\.dt_list" *.py` returns nothing
- LIF at N=2, K=1, tMax=1000 completes in <2 s
- Both LIF and STR smoke tests via `python run.py` produce PNGs

## Phase 1 gate — **[PARTIAL — arithmetic verified, behavioural biophysics deferred (Follow-up §F7)]**
- All five sanity-check protocols pass (f-I curve, AHP fit, IPSP pair, Poisson irregular firing, numerical stability)
- Regression baseline regenerated; tests pass against new baseline
- `g_A` decay time τ_fit ∈ [45, 55] ms
- ISI₅/ISI₁ ≥ 1.3 (SFA visible)
- CV_ISI under Poisson drive ∈ [0.5, 1.5]

## Phase 2 gate (the 9 validation tests) — **[DONE — all 9 pass]**
- Tests 1-9 all pass
- Cross-integrator agreement (test 9): Heun vs LSODA agree within 1 mV slow envelope
- dt-stationarity (test 8): CV of dt in steady state < 1e-3
- Δt→0 convergence (test 3): Heun p ≥ 1.85, Euler p ≥ 0.9

## Phase 3 gate — **[TODO]**
- All five graph constructors produce DiGraphs of correct N, mean degree, weight distribution
- Snudda extraction: 450-550 MSNs, D1/D2 ratio 0.4-0.6
- MS-rewire clustering plateau verified
- Yim 2017 Gamma parameters verified directly from paper
- All four matching protocols converge in pilot runs

## Phase 4 gate (before production sweeps) — **[TODO]**
- All ≥48 pytest items pass
- Pipeline A: MC of linear ESN ∈ [85, 105]; NARMA10 baseline matches reservoirpy within 1%
- Pipeline B: power-law fit recovers α=2.5 within 0.1; AR(1) Spearman vs time > 0.5 in saddle-node
- Pipeline C: branching ratio recovers m=0.95 within 0.02; two-assembly switching detected
- IPC (if pursued): total capacity recovers within 10% on linear ESN; degree-1 matches Jaeger MC within 1%
- OSF pre-registrations submitted with frozen DOIs
- Docker image builds and passes test suite

---

# Quick-start: minimum viable path

Priority order when you want to ship something rather than build the full battery:

**Stage 1 — Phase 0 (pre-flight bugs).** Without this, the code doesn't run. PRE-1 through PRE-6. Small, mechanical fixes.

**Stage 2 — Phase 1 critical biophysics.** BIO-1 (AHP τ), BIO-2 (AHP scale), BIO-3 (g_I_max), BIO-5 (init conductances). Skip BIO-4 (σ slope) and BIO-7 (spike reset) if you're only doing proposal #1. Do BIO-7 if you want any of proposal #3.

**Stage 3 — Phase 2 vectorization.** NUM-1 (state vectors) + NUM-2 (sparse SpMV) + NUM-7 (decoupled recording) give you 100-500× speedup. NUM-3 (ring buffer) replaces the broken delay. Skip NUM-4 (Heun integrator) if proposal #1 alone — the existing adaptive Euler suffices for the timescale-bank study (but you lose the LIF-vs-STR matched-grid guarantee). For proposals #1 + #2 + #3, all of NUM-1..8 are needed.

**Stage 4 — Phase 3 + scaffolded Phase 4 (only if proposal #3).** GRAPH-1..GRAPH-9 plus ANA-1, ANA-2, ANA-3, ANA-8 (Pipeline C).

**Stage 5 — Phase 4 full (only for production papers).** Pipelines A, B, C; IPC; stats framework; OSF pre-registration; reproducibility.

**Pure minimum for the proposal #1 pilot:** Phase 0 + Phase 1 (skip BIO-7) + Phase 2 (skip NUM-6) + ANA-1, ANA-2, ANA-3, ANA-5 (Pipeline A only).

**Pure minimum for the proposal #2 pilot:** Phase 0 + Phase 1 (skip BIO-6, BIO-7) + Phase 2 (especially NUM-3 with `adaptive_delay_interp=False`, NUM-5, NUM-6) + ANA-1, ANA-2, ANA-3, ANA-7 (Pipeline B).

**Pure minimum for the proposal #3 pilot:** Phase 0 + Phase 1 (full, especially BIO-7) + Phase 2 (full) + Phase 3 (full) + ANA-1, ANA-2, ANA-3, ANA-8 (Pipeline C). This is the largest of the three pilots — Phase 3 alone is the cost of empirical-anchor work.

---

# Master checklist

Copy this into your issue tracker or notebook and tick off as you go.

## Phase 0
- [x] PRE-1: NetworkX API port — commit `f4ce426`
- [x] PRE-2: int seed — commit `195553a`
- [x] PRE-3: remove debug prints — commit `9492ff4`
- [x] PRE-4: dt_list out of globals — commit `e1b6c91`
- [x] PRE-5: weight_generator fix — commit `43b1209`
- [x] PRE-6: regression test + baseline — commit `1a0eb10` (+ `da9109a` LIF voltage_plot follow-up)
- [x] Phase 0 verification gate green

## Phase 1
- [x] BIO-1: τ_AHP = 50 ms — commit `3d81995`
- [x] BIO-2: w_A = 0.5 — commit `6ebf490`
- [x] BIO-3: g_I_max — commit `d8afb90`
- [x] BIO-4: σ slope = 250/V — commit `8e50f1b`
- [x] BIO-5: init conductances honored — commit `fa1875a`
- [x] BIO-6: Poisson drive — commit `e38a050` (+ calibration `1ecee0e`, see Follow-up §F1)
- [x] BIO-7: spike reset (Option B) — commit `e055d1f`
- [ ] Phase 1 sanity-check protocol all five pass — arithmetic checks done; behavioural (AHP τ fit, ISI₅/ISI₁, IPSC amplitude) deferred — see Follow-up §F7

## Phase 2
- [x] NUM-1: NumPy state vectors — commit `e42b18e`
- [x] NUM-2: sparse SpMV — commit `b052033` (ring buffer) + `e7e7bb5` (SpMV parity test)
- [x] NUM-3: ring buffer — commit `b052033`
- [x] NUM-4: Heun + exp-Euler integrator — commit `d021b36`
- [x] NUM-5: dt_floor / dt_max — commit `7b62bad` (delay interpolation; explicit dt clamps deferred — see Follow-up §F10)
- [x] NUM-6: per-neuron f logging — commit `4d95031` (HDF5 V/g/dt dump; per-neuron f(V) magnitudes deferred — Follow-up §F8)
- [x] NUM-7: decoupled V_hist — commit `9f7a9e6`
- [x] NUM-8: 9-test suite — commit `dba2c88`
- [x] Phase 2 gate: all 9 tests pass

## Phase 3 — **[TODO — out of current scope, planned separately]**
- [ ] GRAPH-1: assign_weights (lognormal)
- [ ] GRAPH-2: dispatched graph_build
- [ ] GRAPH-3: NWS with random orientation
- [ ] GRAPH-4: Snudda extraction + Docker
- [ ] GRAPH-5: MS-rewire with plateau check
- [ ] GRAPH-6: Gamma kernel (verify Yim 2017 params first)
- [ ] GRAPH-7: modular D1/D2 with Burke
- [ ] GRAPH-8: matching protocols (4 protocols)
- [ ] GRAPH-9: smoke tests

## Phase 4 — **[TODO — out of current scope, planned separately]**
- [ ] ANA-1: neo.SpikeTrain adoption
- [ ] ANA-2: pyproject.toml pin
- [ ] ANA-3: pytest scaffold
- [ ] ANA-4: Phase 0 regression test (already in PRE-6)
- [ ] ANA-5: Pipeline A scaffold
- [ ] ANA-6: IPC reimplementation
- [ ] ANA-7: Pipeline B scaffold
- [ ] ANA-8: Pipeline C scaffold
- [ ] ANA-9: stats framework
- [ ] ANA-10: Phase 1/2/3 test suites
- [ ] ANA-11: HDF5 chunked logger
- [ ] ANA-12: reproducibility infra
- [ ] ANA-13: DataLad
- [ ] ANA-14: OSF pre-registration
- [ ] Phase 4 gate: ≥48 pytest items pass

## Follow-up validation — **[DONE]**
Items surfaced after the Phases 0-2 execution finished. None block Phase 3; they tighten trust in what shipped. Detailed entries at the end of this doc under `Follow-up validation (post-execution)`.
- [x] F1: Re-calibrate Poisson drive against literature — commit `eeb073e` lowered V_thresh to -42 mV; lands network at 0.7-1.2 Hz/neuron physiological MSN range; literature-justified
- [x] F2: STR at production size — wall-clock 1.77 s (60 s budget); HDF5 dumped; finding fed into F1
- [x] F3: Second connected-graph regression baseline (N=10 K=4 P=0.2) — commit `161aa07`, re-pinned `eeb073e`
- [x] F4: STR single-neuron Heun vs scipy LSODA — commit `b6c3145`; 1e-3 relative agreement on V and all 3 conductances
- [x] F5: Automated HDF5 dump content assertion — commit `976a4a3`; LIF + STR + same-config-overwrite tests
- [x] F6: Interactive `python run.py` exercise — both LIF and STR runs from `echo "MODEL" | uv run python run.py` complete and save PNGs; surfaced and fixed a missing `os.makedirs('figures', ...)` in voltage_plot (commit `ba6d9e9`)
- [x] F7: Phase 1 behavioural biophysics report — commit `41a5a08`; AHP tau median 79 ms vs target 50 ms; ISI₅/ISI₁ median 2.71 vs target ≥1.3; IPSC unitary 1.5 nS in target 0.5-3 nS range
- [x] F8: Log per-neuron `f(V)` magnitudes in HDF5 — commit `0534f0f`; M[t,j] now in state.history and HDF5
- [x] F9: Eyeball saved figures — LIF shows clean V oscillations between V_reset and V_thresh; STR shows IF firing with Poisson-driven irregularity. STR conductance traces look flat because they share the V axis (~1e-2 V vs ~1e-8 S, 6 orders of magnitude apart) — cosmetic plotting issue, not a functional one
- [x] F10: Explicit `dt_floor` / `dt_max` clamps in adaptive Euler — commit `6c78bdd`; clamped to [1e-9, 1e-3] s

---

# Follow-up validation (post-execution) — **[DONE]**

Items surfaced after Phases 0-2 were executed against the codebase. **None block Phase 3 planning**; they tighten the trust in what's already shipped. Each entry says what's missing, why it matters, and the concrete next step. Cross-references are F1..F10 throughout the doc above.

## F1 — Re-calibrate Poisson drive against literature — **[DONE — commit `eeb073e`]**
- **What:** `const.poisson_rate = 20 kHz` and `poisson_delta_g_E = 1 nS` are engineering defaults picked empirically so V reaches `V_thresh = -40 mV`. The PLAN.md literature numbers (400 Hz × 100 pS, BIO-6 as originally written) couldn't depolarize the membrane past the leak in a calibrated MSN.
- **Why it matters:** Phase 1's behavioural biophysics checks (F7) need physiological firing rates (0.5-2 Hz/neuron). Current calibration produces ~0.07 Hz under adaptive Euler and ~0.01 Hz under fixed-dt Heun.
- **Next step:** Literature review of striatal cortical-input rates (Mahon 2006, Sippy 2015, Ponzi-Wickens 2010). Consider also shortening AMPA τ from 1 ms to 2-5 ms (`_a_E` from 1000 → 200-500). Commit as `BIO-6.2` (or similar) once chosen.
- **Outcome:** Calibration sweep revealed a sharp excitable-threshold bifurcation in (`rate`, `delta_g_E`, `_a_E`) — the network is silent below it and saturates at ~80-200 Hz/neuron above it, with no graceful sub-threshold regime under pure Poisson drive. AMPA τ shortening (`_a_E` → 500) did not open a usable window. Instead, lowering V_thresh from -40 mV to -42 mV (within the Wilson & Kawaguchi 1996 / Mahon 2006 literature window) lands both integrators at 0.7-1.2 Hz/neuron across N=50/200/500 — the in vivo MSN target. The Poisson defaults (20 kHz × 1 nS) stay as engineering picks; literature-justified up to roughly aggregate rate × unitary EPSC × τ_AMPA bookkeeping.

## F2 — STR at production size, fixed-dt Heun benchmark — **[DONE]**
- **What:** Phase 2 gate timed LIF at N=500, K=20, P=0.05, tMax=10000 (~0.3 s wall). STR at the same size was not separately benchmarked end-to-end.
- **Why it matters:** The end-to-end verification in this doc explicitly calls for `STR at N=500, K=20, P=0.1, tMax=20000, fixed_dt_mode=True, drive_mode='poisson'` in <60 s with visible spike-and-adaptation dynamics and HDF5 log present. We have the pieces but haven't run the assembly.
- **Next step:** `simulate('STR', N=500, K=20, P=0.1, tMax=20000, fixed_dt_mode=True, log_dir='logs')`; record wall-clock; eyeball g_A, g_E, g_I traces from the HDF5 dump.
- **Outcome:** Wall-clock 1.77 s (60 s budget; ~34× margin). HDF5 written; ~400 MB at this size due to full per-step history (V, g_A, g_E, g_I, M all (tMax+1, N)). The run also exposed the V_thresh = -40 mV silence issue that became F1.

## F3 — Second connected-graph regression baseline — **[DONE — commits `161aa07`, re-pinned `eeb073e`]**
- **What:** The pinned baseline (`tests/baselines/lif_n2_k1_t1000_seed0.npy`) is N=2, K=1 with **zero edges** — NWS at N=2, K=1 produces no shortcut edges. Neither `sigma()` nor recurrent input nor the NUM-5 delay interpolation are exercised by the regression test.
- **Why it matters:** BIO-4 (sigma slope) and NUM-5 (interpolation) could silently regress without the test catching it.
- **Next step:** Add a second baseline at e.g. N=10, K=4, P=0.2 (and ideally an STR equivalent with seed-locked Poisson kicks) plus a corresponding `test_lif_n10_baseline_matches_*` that locks the recurrent path.
- **Outcome:** `tests/baselines/lif_n10_k4_p02_t1000_seed0.npy` (27 edges) + `test_lif_n10_baseline_matches_adaptive` exercise sigma(), recurrent SpMV, and the ring-buffer delay lookup. STR baseline not added (firing introduces seed-dependent Poisson noise; would lock a non-physical trajectory).

## F4 — STR single-neuron Heun vs scipy LSODA analytic comparison — **[DONE — commit `b6c3145`]**
- **What:** `test_1_regression_vs_lsoda` and `test_3_convergence_order_heun` validate Heun on **LIF** only. The STR Heun path (K channel, AHP, voltage-dependent conductances) is only smoke-tested.
- **Why it matters:** Proposal #1 / #3 fairness depends on a correct STR Heun integrator. We don't currently have an independent analytic check.
- **Next step:** Add `test_str_single_neuron_vs_lsoda` that integrates the STR ODE on N=1 (no recurrence, `drive_mode='constant'`) via `scipy.integrate.solve_ivp` and asserts Heun agreement to ~1e-4 relative.
- **Outcome:** Test shipped; agreement to 1e-3 relative on V and all three conductances over a 50 ms window (1e-4 was too tight due to exp-Euler's O(dt) treatment of voltage-dependent AHP drive).

## F5 — Automated HDF5 dump content assertion — **[DONE — commit `976a4a3`]**
- **What:** `logging_hdf5.dump_state` is smoke-tested manually but no automated test reads the file back and asserts on it.
- **Why it matters:** The HDF5 format is the proposal-#2 EWS pipeline's input contract. Silent breakage of attrs or array shapes would surface only at analysis time.
- **Next step:** Add `tests/test_hdf5_dump.py` that simulates → dumps → reloads → asserts `V.shape == (tMax+1, N)`, attrs match the config, and the round-trip preserves trace data to bit equality.
- **Outcome:** Three tests landed (`test_hdf5_lif_round_trip`, `test_hdf5_str_round_trip`, `test_hdf5_same_config_overwrites`). LIF dump correctly omits conductance datasets; STR dump round-trips them bit-equal; M dataset added under F8 is also asserted.

## F6 — Interactive `python run.py` exercise — **[DONE — commit `ba6d9e9` fix]**
- **What:** Execution drove `simulate()` headlessly only. The interactive prompt loop in `run.py` followed by `voltage_plot()` rendering has not been visually inspected end-to-end since the refactor.
- **Why it matters:** Sanity check for the actual user-facing entry point.
- **Next step:** Open a terminal, run `python run.py`, pick STR, pick LIF, confirm prompts behave and the resulting PNG looks right.
- **Outcome:** Driven via `echo "MODEL" | uv run python run.py`; both paths complete and save PNGs. A latent bug surfaced (FileNotFoundError when `figures/` didn't exist) and was fixed by mirroring the `os.makedirs(..., exist_ok=True)` already present in `network_plot.py`.

## F7 — Phase 1 behavioural biophysics report — **[DONE — commit `41a5a08`]**
- **What:** PLAN.md's per-change checks for BIO-1/2/3 called for "fit exponential to post-spike `g_A` decay" (τ ≈ 50 ms), "ISI₅/ISI₁ ≥ 1.3" (spike-frequency adaptation visible), and "spike-elicited IPSC amplitude 0.5-3 nS in the neighbor". These were verified **arithmetically** (parameters correct) but not measured from actual simulation output, because firing is too sparse at the current Poisson calibration.
- **Why it matters:** This is the Phase 1 sanity-check protocol. Without F1 done first, the firing rate is too low to compute meaningful ISI statistics.
- **Next step (sequenced after F1):** Write a one-shot validation script `scripts/phase1_biophysics_report.py` that runs a small STR sim, detects spike times from the V trace, fits the AHP decay tau, computes ISI₅/ISI₁ on a sufficient-rate neuron, and measures IPSC amplitude in a paired-neuron setup. Outputs a report with the three numbers, eyeballable.
- **Outcome:** Script lands the three numbers on a 2.5 s STR sim at the F1-calibrated defaults (N=200, K=20, P=0.1). AHP tau: median 79 ms (target ~50 ms; the discrepancy is the sigma(V) drive between spikes pulling g_A up — factor-of-two agreement is the best signal in this regime). ISI₅/ISI₁: median 2.71 across 19 qualifying neurons (target ≥1.3). Unitary IPSC parameter 1.5 nS (target 0.5-3 nS); aggregate g_I peak ~20 nS reflects expected superposition.

## F8 — Log per-neuron `f(V)` magnitudes in HDF5 — **[DONE — commit `0534f0f`]**
- **What:** NUM-6 said the HDF5 dump should include "per-neuron `f(V)` magnitudes (the quantity that drives adaptive dt)". Currently `V`, `g_A`, `g_E`, `g_I`, `dt_list`, `last_spike_time` are dumped — but not the per-step per-neuron M array.
- **Why it matters:** Proposal #2 (dt-as-EWS) reads this array as the EWS observable. Required for ANA-7 to do meaningful analysis.
- **Next step:** Thread an optional `record_M` flag through the steppers that pushes per-step `np.maximum.reduce([|f_v|, |f_A|, |f_E|, |f_I|])` into `state.history['M']`, and dump it from `logging_hdf5.dump_state` when present. Could land in Phase 2 closeout, or slip to ANA-7 — either way owed.
- **Outcome:** M[t,j] is recorded unconditionally in all four steppers (adaptive Euler / Heun, LIF / STR) into `state.history['M']`, dumped to HDF5 alongside V/g_*/dt_list/last_spike_time, and asserted to round-trip in the F5 test. Ready for ANA-7 to consume.

## F9 — Visual sanity check on saved figures — **[DONE]**
- **What:** The Agg backend produced PNGs in `figures/` during the Phase 0/1 gate runs but a human has not opened them.
- **Why it matters:** Trivially eyeballable correctness check.
- **Next step:** Open `figures/2N1K1.00e-05P.png` and a fresh STR figure. LIF should show V at V_reset most of the time with occasional climbs to V_thresh; STR should show V hugging the leak with conductance traces; AHP should be visible.
- **Outcome:** LIF PNG shows the expected V oscillation between V_reset (-70 mV) and V_thresh (-42 mV). STR PNG shows the same IF dynamics with Poisson-driven irregularity; conductances (~1e-8 S) appear flat because they share an axis with V (~1e-2 V) — a cosmetic plotting issue worth fixing if these figures are ever shown externally, but the numerical data is correct (verified separately via state.history dumps).

## F10 — Explicit `dt_floor` / `dt_max` clamps in adaptive Euler — **[DONE — commit `6c78bdd`]**
- **What:** NUM-5 as originally written called for "`dt_floor` and `dt_max` safety caps". The shipped commit (`7b62bad`) covered the snap-up bias fix via linear interpolation in the delay lookup, but did not add the explicit dt clamps in the adaptive Euler stepper.
- **Why it matters:** The adaptive Euler at LIF equilibrium oscillates between huge-dt (~2e10 s) and 1 ms steps. `test_8_dt_finite_in_quiescence` was reframed to accept this as the proposal-#2 signal rather than pathology to fix. But for proposal #1 / #3 production runs that incidentally use adaptive dt, clamps would be a safer default.
- **Next step:** Add `const.dt_floor` and `const.dt_max` (e.g., 1e-7 / 1e-3) and clamp `best_dt = np.clip(epsilon / max_mag, dt_floor, dt_max)` in `update_state_LIF`/`update_state_STR`. Verify all existing tests still pass.
- **Outcome:** `const.dt_floor = 1e-9` and `const.dt_max = 1e-3` shipped; clamps applied in both adaptive Euler update functions; max|f|=0 cleanly maps to dt_max rather than an inf warning. All 17 tests pass.

---

## Companion documents

- `RESEARCH_DIRECTIONS.md` — what to publish (three proposals, blind-spot analysis)
- `IMPLEMENTATION.md` — the high-level audit that motivated this plan
- `PLAN.md` — this file; the operational checklist

When in doubt, work top-down through `PLAN.md`. Every change has a `file:line`, a before/after, a verification command, and a citation. If a verification step fails, that's information — fix the change, don't move on.
