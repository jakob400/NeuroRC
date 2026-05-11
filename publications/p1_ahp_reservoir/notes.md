# P1 — AHP reservoir notes

## Status

**Pilot-ready post fix-B (2026-05-11).** α×β grid is 24/24 feasible
under the slow-K + OU-drive combo. Pilot infrastructure (LIF-het,
LIF-ALIF, IPC reimplementation) still needs to be built.

## Working title

> *AHP conductances as a network-level timescale reservoir: biophysical
> adaptation as the mechanism for the Bernacchia timescale reservoir
> in coupled small-world networks.*

## One-sentence claim

In a fixed small-world reservoir, biophysical AHP and voltage-gated
potassium conductances jointly produce a broader per-neuron
autocorrelation-timescale distribution and higher Jaeger memory capacity
than any rate-matched LIF reservoir — including LIF with a tuned
per-neuron leak distribution — establishing biophysical adaptation as
the network-level mechanism for the timescale reservoir originally
described in single neurons by Bernacchia et al. (2011).

## Target venue

- Primary: Neural Computation — ~40-50%
- Fallback: Frontiers in Computational Neuroscience — ~60-70%

## What's still needed before pilot

1. LIF-het (per-neuron leak conductance distribution) variant.
2. LIF-ALIF (adaptive threshold) variant for the falsification control.
3. Firing-rate matching protocol (binary search on drive). Fix B may
   have made this unnecessary — verify with a uniform-drive grid first.
4. `src/metrics/pipeline_a_reservoir.py`: ridge regression, LOO-CV,
   memory-capacity (MC) and NARMA-10 benchmark.
5. `src/metrics/ipc.py`: Dambre 2012 information processing capacity
   decomposition. Heaviest single piece of new code in the whole
   project (~3-5 days).

## Falsification criterion

If LIF-het matches STR on MC within 20%, OR if the per-neuron τᵢ
distribution from STR is not visibly broader than LIF-het, the paper
does not exist. Pivot to a τᵢ-shape-only claim or abandon.

## Top threats

1. LIF-het matches STR (doc estimates 30% likely; Perez-Nieves 2021
   is the real adversary).
2. Scoop from Goodman or Salaj/Maass labs in ~6 months.

## Notes / pointers

- Original proposal text: `../../docs/RESEARCH_DIRECTIONS.md` §Proposal 1.
- Bernacchia 2011 (Nature Neuroscience): single-neuron timescale
  reservoir motivation.
- Perez-Nieves 2021 (Nat Comms): "Neural heterogeneity promotes robust
  learning" — must address why LIF-het isn't enough.
