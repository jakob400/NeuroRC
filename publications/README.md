# publications/

Self-contained working directories for each manuscript this project is
producing. Each paper subdirectory has the same shape:

```
publications/<id>/
├── manuscript/    LaTeX sources + bibliography
├── figures/       Paper-grade figures (PNG + SVG). Tracked, NOT gitignored.
├── data/          CSVs + raw stdout dumps backing every numerical claim.
├── scripts/       Paper-specific scripts (e.g. make_figures.py).
└── notes.md       Per-paper working notes, status, and outline.
```

## Current papers

| ID | Title | Status |
|---|---|---|
| `p0_methods` | Bifurcation infeasibility + dt folklore quantification (methods paper) | Pilot data in repo; manuscript to be drafted. ~2-3 weeks. |
| `p1_ahp_reservoir` | AHP conductances as a network-level timescale reservoir | Pilot-ready post fix-B; LIF-het + IPC reimpl needed. ~4-6 months. |
| `p3_connectome_atlas` | Necessary structural features for striatal dynamics: a null-model atlas | Blocked on fix C (Snudda + GRAPH-8). ~5-6 months once unblocked. |

Proposal #2 (dt-as-observable) was abandoned standalone after fix B
narrowed the dt observable's dynamic range; the material salvaged into
`p0_methods` as the "dt folklore quantification" thread.

## Regenerating a paper's figures

Each paper's `scripts/` has a `make_figures.py` that anchors its output
to the paper directory (not cwd). To regenerate from a clean checkout:

```bash
uv run python publications/p0_methods/scripts/make_figures.py
```

Wall clock ~3-4 min for p0 (24-cell alpha-beta grid is the bottleneck).

## See also

- `../docs/PUBLICATIONS.md` — per-paper claims, target venues, falsification criteria.
- `../docs/NEXT_STEPS.md` — current state of the project and recommended sequencing.
- `../docs/DIAGNOSTICS.md` — diagnostic findings backing the P0 manuscript.
- `../docs/teX.md` — LaTeX cheat-sheet used across all manuscripts.
