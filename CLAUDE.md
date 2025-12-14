# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NeuroRC (NeuroRegionCompute) is a neural network simulation tool that models spiking neuron dynamics using NetworkX graphs. It implements two neuron models:
- **STR (Striatum)**: Full biophysical model with voltage and conductance dynamics (excitatory, inhibitory, potassium/AHP channels)
- **LIF (Leaky Integrate-and-Fire)**: Simplified model with voltage dynamics only

## Running the Simulation

```bash
python run.py
```

The simulation prompts for model selection (STR or LIF) and runs for `tMax` timesteps (configured in `const.py`).

## Architecture

**Entry point**: `run.py` - Interactive CLI that builds the network, runs simulation, and generates plots

**Core simulation flow**:
1. `graph_build.py`: Creates Newman-Watts-Strogatz small-world network using NetworkX
2. `weight_generator.py`: Assigns synaptic weights to edges
3. `update_functions.py`: Contains `update_state_STR()` and `update_state_LIF()` which compute voltage/conductance evolution per timestep
4. `math_functions.py`: Sigmoid activation functions (`sigma`, `sigma_0`), delay calculations, and noise generation

**Configuration**: `const.py` - All simulation parameters (time constants, reversal potentials, conductances, network topology N/K/P)

**Visualization**:
- `dynamic_voltage_plot.py`: Plots voltage and conductance traces over time
- `network_plot.py`: Generates network state snapshots (for animation)

## Key Implementation Details

- Uses adaptive timestep (dt) with dynamic protection: `dt = epsilon / max(|func|)` to maintain numerical stability
- Node attributes store time-series data as lists (e.g., `G.node[j]['voltage']` is a list of voltages at each timestep)
- Delay function computes how many timesteps back to look for synaptic delays based on accumulated dt values
- Figures saved to `figures/` directory with naming pattern `{N}N{K}K{P}P.png`

## Dependencies

- networkx
- numpy
- matplotlib
