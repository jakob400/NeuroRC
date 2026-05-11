# P0 — Methods paper notes

## Status

**Pilot data complete; manuscript drafting next.** All four diagnostic
findings (D1 resolved, D2 resolved, D3 honestly worsened, D4 resolved)
have pre/post fix-B numbers committed. Figures and CSVs are in
`figures/` and `data/`.

## Working title

> *Bifurcation-induced infeasibility regions in threshold-reset spiking-
> network parameter sweeps: a calibration protocol and a dt-as-stiffness
> folklore quantification.*

## One-sentence claim

Spiking-network parameter sweeps in threshold-reset models have intrinsic
bifurcation-induced infeasibility regions that biophysical up/down state
mechanisms eliminate; the adaptive-solver `dt(t)` stream — sometimes
cited as a free dynamical observable — has a measurable, quite narrow
dynamic range that *narrows further* under biophysical realism.

## Target venue

- Primary: Frontiers in Computational Neuroscience (Methods track) — ~50-60%
- Fallback: PLOS Computational Biology (Methods)

## Manuscript outline

| Section | Source material | Status |
|---|---|---|
| Intro: Söderlind/Scheffel framing | `../../docs/RESEARCH_DIRECTIONS.md` §Proposal 2 citations | Outline only |
| Methods: model + integrators | `../../CLAUDE.md`, `src/{state,integrators,update_functions}.py` | Code present |
| Result 1: Bifurcation infeasibility regions | `figures/alpha_beta_heatmap.{png,svg}`, `data/alpha_beta_grid_{pre,post}.csv`, `../../docs/DIAGNOSTICS.md` D2 | Figures and CSVs done |
| Result 2: V_thresh sensitivity knife-edge | `figures/v_thresh_sensitivity.{png,svg}`, `data/v_thresh_sweep_{pre,post}.csv`, `../../docs/DIAGNOSTICS.md` D4 | Figures and CSVs done |
| Result 3: Bistability rescues α×β grid | `figures/v_histogram.{png,svg}`, `data/v_histogram_post.csv` | Figures and CSVs done |
| Result 4: dt-folklore quantification | `figures/dt_kde.{png,svg}`, `data/dt_ranges.csv`, `../../docs/DIAGNOSTICS.md` D3 | Figures and CSVs done |
| Calibration cookbook | `../../scripts/phase1_biophysics_report.py`, `../../scripts/diag_recalibrate_directed.py` | Scripts present |
| Discussion: generalization | Optional Brian2/NEURON portability spike | Not implemented |
| Reproducibility | `scripts/make_figures.py` (single-entry rebuild) | Done |

## Defenses

- "But does this generalize beyond NeuroRC?" → optional ~3-day Brian2 /
  NEURON CVODE single-neuron portability spike. Reproduces the
  log(1/dt) range measurement there; if NeuroRC's narrowness holds, the
  result generalizes. (Not yet implemented.)
- "This is folklore." → Söderlind/Jay/Calvo 2015 and Scheffel 2024
  framed dt-as-stiffness-indicator on single ODEs; the contribution
  here is the spiking-network measurement and the calibration cookbook.

## Falsification criterion

None — this is a measurement paper, not a hypothesis test.

## Reproducibility

Regenerate every figure and CSV from a clean checkout:

```bash
uv run python publications/p0_methods/scripts/make_figures.py
```

Wall clock ~3 min on dev laptop.
