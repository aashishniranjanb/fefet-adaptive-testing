# FeFET Adaptive Testing Framework

This project introduces a cross-layer framework designed for degradation-aware fault modeling and ML-driven adaptive test generation in Ferroelectric Field-Effect Transistor (FeFET) memories. 

As FeFET technologies undergo extensive program/erase cycles, they experience significant physical degradation (threshold voltage shifts, interface trap generation). This toolchain directly addresses the challenge of deteriorating memory reliability over time by bridging low-level physical degradation with system-level testing strategies.

## Key Features

1. **Physical Degradation Modeling:** Incorporates models for cycle-dependent degradation, write-history impacts, and temperature sensitivities to extract realistic threshold voltage shifts (ΔVth) alongside device variations and cycle-to-cycle noise.
2. **Dynamic Fault Assignment:** Maps physical shifts into specific fault behaviors such as Read Margin Failures (SDRF), Write Instability (DIRF), Weak Polarization (PPF), and Coupling Data Failures (CDF).
3. **ML-Based Adaptive Test Selection:** Uses a Random Forest classifier trained on degradation data to dynamically predict and select the optimal memory test pattern (e.g., MATS+, March C-, Adaptive tests), maximizing fault coverage.
4. **End-to-End Pipeline:** Seamlessly simulates the entire feedback loop from dataset generation, ML training, coverage calculation, and final result visualization.

## Getting Started

1. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run Pipeline:**
   ```bash
   python run.py
   ```
   Executing `run.py` will generate the dataset, assign labels based on predicted optimal tests, train the ML model, and evaluate the fault coverage of different testing strategies across endurance levels.

## Outputs

After running the pipeline, check the `results/` folder for:
- `coverage_vs_endurance.png`: Fault coverage comparisons across testing algorithms.
- `fault_distribution.png`: Distribution of the mapped faults in the generated dataset.
- `confusion_matrix.png`: Evaluation of the ML model's accuracy.

