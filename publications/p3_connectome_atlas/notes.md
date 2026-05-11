# P3 — Connectome atlas notes

## Status

**Blocked on fix C.** GRAPH-4 (Snudda extraction) and GRAPH-8 (matching
protocols) are still TODO. Six-month scoop clock from the Kotaleski
lab is the principal time pressure. Fix B (already landed) makes the
eventual pilot cheaper but does not unblock the pilot itself.

## Working title

> *Necessary structural features for striatal dynamics: a null-model
> atlas comparing NWS, Snudda, MS-rewire, gamma-kernel, and modular
> nulls under identical biophysical dynamics.*

## One-sentence claim

By running identical biophysical dynamics on five carefully matched
graph nulls — including a Snudda-derived MSN subgraph and its
degree-preserving rewire — we produce the first feature-by-signature
necessity matrix for striatal dynamics, transferring the Gal/Reimann/
Markram 2020 cortical framework to the basal ganglia and answering the
question Carannante 2024 explicitly left open.

## Target venue

- Primary: Network Neuroscience — ~50%
- Fallback: eLife / PLOS Comp Bio — ~25%

## What's still needed

1. GRAPH-4: Snudda Docker pipeline + extraction script. Pinned to
   FrontNeuralCircuits2021 tag, 4+ years old. ~3-5 days of HDF5
   schema-drift work.
2. GRAPH-6: gamma-kernel — blocked on Yim 2017 parameter verification.
3. GRAPH-8: four matching protocols (rate, E-drive, I-drive, variance).
4. `src/metrics/pipeline_c_spikes.py`: NMF assembly detection, Pareto
   ISI fitting, Plenz-style avalanche-modulated drive, Clauset
   power-law fit.

## Falsification criterion

Cliff's δ < 0.8 between NWS and Snudda dwell-time distributions in the
pilot → publish as a Brief Communication ("Striatal assembly switching
is robust to connectivity topology") and stop. Either branch
publishes.

## Top threats

1. Kotaleski-lab releases a Carannante-dynamics extension within 6
   months (~30% likely). Mitigation: speed, early email to
   Hjorth/Kotaleski.
2. NWS vs Snudda dwell-time distributions don't differ. Mitigation:
   already a Brief Communication fallback.
3. Snudda extraction infeasible in time. Mitigation: synthetic
   distance-dependent calibrated to Hjorth 2020 connection
   probabilities (Belić 2024's approach).

## Notes / pointers

- Original proposal text: `../../docs/RESEARCH_DIRECTIONS.md` §Proposal 3.
- Gal et al. 2020 (Cell Reports): cortical-microcircuit framework
  this paper transfers.
- Carannante et al. 2024 (J Neurosci): striatal microcircuit work
  that explicitly left the connectome-comparison question open.
