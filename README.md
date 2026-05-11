# NeuroRC

Spiking-neuron simulation on NetworkX graphs. Two neuron models:

- **STR** — five-state biophysical MSN (V + AHP + voltage-gated K +
  slow K inward rectifier + cortical drive), with up/down state
  bistability under OU cortical drive.
- **LIF** — leaky integrate-and-fire baseline.

Both run on the same graph topology so they can be compared under
matched conditions.

## Quick start

```bash
uv sync --extra dev
uv run pytest            # 56 tests, ~6 s
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
| [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) | **Start here.** Where the project stands today, what's broken, what to do next, and which paper(s) are publishable. |
| [`docs/PUBLICATIONS.md`](docs/PUBLICATIONS.md) | Expected paper portfolio: four candidate papers (P0–P3), their claims, falsification criteria, time-to-manuscript, and which engineering fixes each one needs. |
| [`docs/RESEARCH_DIRECTIONS.md`](docs/RESEARCH_DIRECTIONS.md) | Three publishable research directions with citations, kill-paper analyses, and pilot designs. |
| [`docs/PLAN.md`](docs/PLAN.md) | Five-phase operational plan with per-item status, file:line references, and verification commands. |
| [`docs/DIAGNOSTICS.md`](docs/DIAGNOSTICS.md) | Diagnostic runs with pre/post fix-B before/after tables. Read alongside `docs/NEXT_STEPS.md`. |
| [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md) | The five-agent audit that produced `docs/PLAN.md`. |
| [`docs/teX.md`](docs/teX.md) | LaTeX cheat-sheet used across all manuscripts in `publications/`. |
| [`publications/README.md`](publications/README.md) | Multi-paper writing workspace. |
| [`CLAUDE.md`](CLAUDE.md) | Project architecture overview. |

### Companion executables

- `uv run pytest` — 56 tests, ~6 s
- `uv run python run.py` — interactive CLI (LIF/STR prompt)
- `uv run python -m scripts.phase1_biophysics_report` — biophysics
  sanity (BIO-1/2/3 + AHP τ + IPSC scale targets)
- `uv run python -m scripts.diag_*` — the four diagnostics
- `uv run python publications/p0_methods/scripts/make_figures.py` —
  regenerates every P0 methods-paper figure (in
  `publications/p0_methods/figures/`) and CSV (in
  `publications/p0_methods/data/`); ~3-4 min wall clock.
- `uv run python -m scripts.proposal2_pilot_smoke` — EWS pipeline smoke test

## Repository layout

```
.
├── src/                      # Simulator core (importable as flat modules)
│   ├── const.py              # All simulation parameters
│   ├── simulate.py           # Headless entry: simulate(model, ...)
│   ├── graph_build.py        # Dispatched graph constructors
│   ├── weight_generator.py   # assign_weights(distribution='lognormal'|...)
│   ├── state.py              # State dataclass + sparse adjacency builder
│   ├── integrators.py        # Heun fixed-dt (default) + adaptive Euler
│   ├── update_functions.py   # Per-step state updates
│   ├── delay_buffer.py       # Ring buffer for delayed voltage lookups
│   ├── math_functions.py     # Sigmoids, sigma_KIR, delay() helper
│   ├── logging_hdf5.py       # Per-run HDF5 dump
│   ├── dynamic_voltage_plot.py
│   ├── network_plot.py
│   └── metrics/              # EWS detectors, Kuramoto oracle, stats
├── publications/             # One subdir per manuscript (P0 / P1 / P3)
│   ├── p0_methods/{manuscript,figures,data,scripts,notes.md}
│   ├── p1_ahp_reservoir/{...}
│   └── p3_connectome_atlas/{...}
├── docs/                     # Project-management markdown
├── scripts/                  # General diagnostics (diag_*, phase1_*, proposal2_*)
├── tests/                    # 56 tests; conftest.py adds src/ to path
├── run.py                    # Interactive CLI wrapper
├── README.md                 # This file
├── CLAUDE.md                 # Architecture overview for Claude Code
├── pyproject.toml            # uv-managed env (deps + pytest config)
└── uv.lock                   # Pinned dependency resolution
```
