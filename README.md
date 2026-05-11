# NeuroRC

Spiking-neuron simulation on NetworkX graphs. Two neuron models:

- **STR** — full biophysical striatal neuron (V + AHP + voltage-gated
  K + excitatory / inhibitory conductances; Poisson cortical drive).
- **LIF** — leaky integrate-and-fire baseline.

Both run on the same graph topology so they can be compared under
matched conditions.

## Quick start

```bash
uv sync --extra dev
uv run pytest            # 49 tests, ~1.7 s
uv run python run.py     # interactive CLI; prompts STR/LIF
```

Or, headless:

```python
from simulate import simulate
G, state = simulate('STR', N=500, K=20, P=0.1, tMax=20000,
                    seed=0, fixed_dt_mode=True, log_dir='logs')
```

## Where to read what

| Document | When to read it |
|---|---|
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | **Start here.** Where the project stands today, what's broken, what to do next, and which paper(s) are publishable. |
| [`PUBLICATIONS.md`](PUBLICATIONS.md) | Expected paper portfolio: four candidate papers (P0–P3), their claims, falsification criteria, time-to-manuscript, and which engineering fixes each one needs. |
| [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) | Three publishable research directions with citations, kill-paper analyses, and pilot designs. |
| [`PLAN.md`](PLAN.md) | Five-phase operational plan; 44 atomic changes with per-item status, file:line references, and verification commands. |
| [`DIAGNOSTICS.md`](DIAGNOSTICS.md) | Four diagnostic runs (2026-05-11) that surfaced three project-level constraints. Read alongside `NEXT_STEPS.md`. |
| [`IMPLEMENTATION.md`](IMPLEMENTATION.md) | The five-agent audit that produced `PLAN.md`. |
| [`CLAUDE.md`](CLAUDE.md) | Project architecture overview. |

## Repository layout

```
.
├── const.py                  # All simulation parameters
├── simulate.py               # Headless entry point: simulate(model, ...)
├── run.py                    # Interactive CLI wrapper
├── graph_build.py            # Dispatched graph constructors
├── weight_generator.py       # assign_weights(distribution='lognormal'|...)
├── state.py                  # State dataclass + sparse adjacency builder
├── integrators.py            # Heun fixed-dt (default) + adaptive Euler
├── update_functions.py       # Per-step state updates
├── delay_buffer.py           # Ring buffer for delayed voltage lookups
├── math_functions.py         # Sigmoids, delay() helper
├── logging_hdf5.py           # Per-run HDF5 dump
├── dynamic_voltage_plot.py   # voltage_plot(state) -> PNG
├── network_plot.py           # Network state snapshots
├── metrics/                  # EWS detectors, Kuramoto oracle, stats
├── scripts/                  # diag_*, phase1_biophysics_report, proposal2_*
├── tests/                    # 49 tests across 7 files
├── pyproject.toml            # uv-managed env (deps + pytest config)
└── uv.lock                   # Pinned dependency resolution
```
