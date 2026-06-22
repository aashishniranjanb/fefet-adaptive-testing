# Cross-Layer Degradation-Aware Fault Modeling and Adaptive Test Generation for FeFET Memories

## Overview

This project proposes a TCAD-calibrated, machine-learning-assisted framework for adaptive testing of FeFET non-volatile memories under endurance degradation.

The framework connects:

TCAD Device Simulation → Threshold Voltage Degradation → Functional Fault Modeling → Adaptive Test Selection → RTL Validation

## Toolchain

* Synopsys Sentaurus TCAD
* Cadence Xcelium
* Python
* Scikit-Learn
* NumPy
* Pandas

## Results

* Fault Coverage: 92–95%
* Baseline March C− Coverage: 65%
* Dataset Size: ~3120 samples
* Memory Array: 64 × 64

## Repository Structure

TCAD_WORKFLOW/
data/
src/
results/
paper/

## Run

```bash
python run.py
```
