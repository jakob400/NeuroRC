# CLAUDE.md

Guidance for Claude Code when working with this repo. For *what* to do next see
`NEXT_STEPS.md`; this doc covers *how* the code is laid out and what to know to
edit it safely.

## Project Overview

NeuroRC (NeuroRegionCompute) simulates spiking-neuron dynamics on NetworkX
graphs. Two neuron models:

- **STR (Striatum)** — five-state biophysical MSN model: V, g_A (AHP),
  g_E (cortical drive), g_I (recurrent inhibition), g_KIR (slow K inward
  rectifier; gives up/down state bistability per Wilson & Kawaguchi 1996,
  Mahon 2006).
- **LIF** — leaky integrate-and-fire; one state (V) plus threshold-reset.

Both share: a hard spike-reset (`V_thresh`, `V_reset`, `t_refr`), a delayed
recurrent term via a ring-buffer, and a sparse adjacency (`A[postsyn, presyn]`).

## Running

```bash
uv sync --extra dev
uv run pytest                              # 56 tests, ~6 s
uv run python run.py                       # interactive CLI; prompts STR/LIF
uv run python -m scripts.phase1_biophysics_report
uv run python -m scripts.p0_make_figures   # ~3-4 min, fills figures/p0/
```

Headless:

```python
from simulate import simulate
G, state = simulate('STR', N=500, K=20, P=0.1, tMax=20000,
                    seed=0, fixed_dt_mode=True, log_dir='logs')
```

## Architecture

**Entry points:**
- `simulate.py` — `simulate(model, *, N, K, P, tMax, seed, fixed_dt_mode,
  state_init, log_dir) -> (G, state)`. Headless; tests and scripts go through
  this.
- `run.py` — interactive CLI wrapper around `simulate`.

**Per-step flow:**
1. `graph_build.graph_build(graph_type='nws', ...)` — dispatched graph
  constructor (`nws`, `modular`, `ms_rewire`, `gamma_kernel`, `snudda`).
  Returns a `DiGraph`.
2. `weight_generator.assign_weights(G, distribution=...)` — uniform,
  lognormal (Koos 2004), or Snudda-native distributions.
3. `state.build_state(G, model)` — bundles per-neuron ndarrays (V, g_A, g_E,
  g_I, g_KIR, last_spike_time) plus sparse CSR adjacency `A[postsyn, presyn]`
  plus a `RingBuffer` for delayed voltage lookups.
4. `integrators.step_for(model)` — dispatches to one of:
   - `step_heun_fixed_*` (default): Heun RK2 on V at `const.dt_fixed`,
     exp-Euler on conductances, OU drive on g_E under `drive_mode='ou'`.
   - `step_euler_adaptive_*` (legacy): adaptive Euler with
     `dt = epsilon / max|f|`, clamped to `[dt_floor, dt_max]`.
5. Spike reset: any neuron crossing `V_thresh` is set to `V_reset` and held
   there for `t_refr`.

**Cortical drive modes** (`const.drive_mode`):
- `'ou'` (default post-fix-B): g_E is the cortical drive itself, following
  an Ornstein-Uhlenbeck process with mean `ou_mean=3 nS`, std `ou_sigma=4 nS`,
  `ou_tau=50 ms`. Exact discretization; clamped ≥ 0.
- `'poisson'`: g_E follows AMPA decay with per-step Poisson kicks
  (`poisson_rate=20 kHz`, `delta_g_E=1 nS`). Legacy; produces saturating drive
  that prevents bistability.
- `'constant'`: legacy +I term; mainly used by `test_str_single_neuron_vs_lsoda`.

**Configuration:** `const.py` — every parameter (time constants, reversal
potentials, conductances, network topology N/K/P, drive params, integrator
selection, spike-reset thresholds). Mutated freely by scripts and tests; the
`override` helper in `tests/test_validation.py` shows the snapshot/restore
pattern.

**Visualization:**
- `dynamic_voltage_plot.voltage_plot(state, node=0)` — V + conductance traces.
- `network_plot.py` — network state snapshots (for animation).
- `scripts/p0_make_figures.py` — regenerates every P0 methods-paper figure.

**Logging:** `logging_hdf5.dump_state(state, model, seed, log_dir)` — one
HDF5 per run, file name keyed by a SHA-1 over config + drive params. Dumps V,
all conductances (incl. g_KIR), dt_list, last_spike_time, and per-step
`M[t,j] = max(|f_V|, |f_*|)` (the quantity that drives adaptive dt).

## Key Implementation Details

- **Adjacency convention:** `A[postsyn, presyn] = w` so the recurrent input to
  neuron `j` is `(A @ sigma_delayed)[j]`. NWS is built as undirected then
  given a random orientation per edge (one entry per directed edge); other
  graph types are constructed as `DiGraph` directly.
- **Delays:** ring buffer with linear interpolation lookup at lag `τ_D`.
  Under fixed dt, the lookup is exact at `int(τ_D / dt)` steps back; under
  adaptive dt it interpolates between cumulative-dt slices.
- **Per-neuron state lives in arrays, not on the graph.** `G.nodes[j]`
  carries topology only; per-step V/conductance values come from
  `state.V`, `state.g_*`, and the history dict.
- **Spike detection in analyses:** count crossings of
  `V_reset + 1e-9` from above (`((V[:-1] > V_reset+eps) & (V[1:] <= V_reset+eps)).sum()`).
  Refractory hold makes this an exact spike count.
- **Reproducibility:** `simulate(seed=...)` sets both `random.seed` and
  `np.random.seed`. OU and Poisson kicks both use `np.random.*` and are
  reproducible across runs with the same seed and `drive_mode`.

## Project State (2026-05-11)

- Phases 0-2 (foundation + biophysics + integrator refactor) done.
- Phase 3 shared minimum (graph dispatch + lognormal weights + NWS-as-DiGraph
  + modular SBM + MS-rewire) done.
- **Fix A** (V_thresh recalibration) and **fix B** (slow K + OU drive) done.
  D1/D2/D4 resolved; D3 worsened-but-publishable. See `DIAGNOSTICS.md` for
  before/after numbers.
- P0 (methods paper) is the next deliverable; all repo-side artifacts
  (figures, CSVs, scripts) are committed. Manuscript drafting is off-repo.

## Dependencies

Managed via `uv`; pinned in `pyproject.toml` + `uv.lock`.

- `networkx >= 3` (topology and graph constructors)
- `numpy` (vectorized state)
- `scipy` (sparse adjacency, LSODA reference integrator in tests)
- `h5py` (per-run logging)
- `matplotlib` (figures)
- `pytest` (dev)
