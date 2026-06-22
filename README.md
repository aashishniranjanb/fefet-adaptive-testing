# Cross-Layer Degradation-Aware Fault Modeling and Adaptive Test Generation for FeFET Memories

> A TCAD-calibrated, machine-learning-assisted framework that bridges device-level degradation physics to memory-level adaptive test selection for ferroelectric FET (FeFET) non-volatile memories.

---

## Abstract

Endurance-induced degradation in ferroelectric HfO₂-based FeFETs — driven by charge trapping, domain pinning, and interface-state generation — causes progressive threshold-voltage (V_th) shifts and memory-window collapse. Traditional march-based memory tests apply a fixed test set regardless of the device's degradation state, leaving aging-dependent faults undetected.

This work proposes a **cross-layer framework** that:

1. **Simulates** FeFET degradation using Synopsys Sentaurus TCAD with Preisach ferroelectric polarization and trap models.
2. **Extracts** key reliability metrics — V_th(program), V_th(erase), and the Memory Window (MW) — across endurance cycling conditions.
3. **Maps** TCAD-calibrated V_th shifts to functional fault models (transition faults, read-disturb faults, retention faults, state-coupling faults).
4. **Trains** a Random Forest classifier to predict the most effective test pattern for a given degradation signature.
5. **Evaluates** adaptive test selection against conventional March C⁻, achieving significantly higher fault coverage with fewer test patterns.

---

## Framework Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TCAD Layer (Sentaurus)                       │
│  SDE (Geometry) ──► SDevice (Physics) ──► Inspect (Extraction)     │
│  fefet_sde.cmd       fefet_des.cmd         fefet_extract.tcl       │
│                                                                     │
│  ● Preisach polarization model (HfO₂ ferroelectric region)         │
│  ● Interface traps (Si/SiO₂) + bulk traps (ferroelectric)         │
│  ● Program/Erase pulse sequences with read-back sweeps             │
└────────────────────────────┬────────────────────────────────────────┘
                             │  Vth_prg, Vth_ers, MW
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Fault Modeling Layer (Python)                    │
│                                                                     │
│  vth_extract.py ──► fault_model.py ──► fault_mapper.py             │
│                                                                     │
│  ● Endurance-dependent Vth degradation curves                      │
│  ● Physics-to-fault mapping: ΔVth → {TF, RDF, RF, SCF, IRF}       │
│  ● Parametric fault injection on 64×64 memory array                │
└────────────────────────────┬────────────────────────────────────────┘
                             │  Labeled fault samples
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ML & Adaptive Test Layer (Python)                  │
│                                                                     │
│  generate.py ──► train.py ──► run.py                               │
│                                                                     │
│  ● Dataset: ~3120 samples across 5 endurance bins                  │
│  ● Random Forest classifier (scikit-learn)                         │
│  ● Per-sample optimal test selection                               │
│  ● Coverage evaluation with 95% confidence intervals               │
└────────────────────────────┬────────────────────────────────────────┘
                             │  Adaptive test verdicts
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RTL Validation Layer                           │
│                                                                     │
│  memory.v ── Verilog behavioral model of the FeFET memory array    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Results

| Metric | Value |
|---|---|
| Classifier Accuracy | **87.7%** |
| Adaptive Fault Coverage | **92.2%** |
| Baseline March C⁻ Coverage | **49.2%** |
| Coverage Improvement | **+43 pp** over March C⁻ |
| Dataset Size | 3,120 samples (5 endurance bins) |
| Memory Array | 64 × 64 FeFET cells |
| Endurance Range | 10³ – 10⁶ cycles |

---

## Repository Structure

```
FEFET_ADAPTIVE_TESTING/
│
├── run.py                        # End-to-end pipeline entry point
├── vth_extract.py                # Threshold voltage extraction utilities
├── requirements.txt              # Python dependencies
│
├── src/
│   ├── simulation/
│   │   ├── fault_model.py        # Degradation-aware fault detection logic
│   │   └── labeling.py           # Optimal test labeling per sample
│   ├── fault_models/
│   │   └── fault_mapper.py       # Physics-to-fault-type mapping
│   ├── dataset/
│   │   ├── generate.py           # Synthetic dataset generation
│   │   └── tcad_integration.py   # TCAD CSV → ML feature pipeline
│   ├── ml/
│   │   └── train.py              # Random Forest training & evaluation
│   ├── evaluation/
│   │   └── stats.py              # Statistical metrics (95% CI)
│   └── rtl/
│       └── memory.v              # Verilog behavioral memory model
│
├── data/
│   ├── dataset.json              # Generated labeled dataset
│   ├── tcad_data.csv             # Raw TCAD simulation parameters
│   ├── generated_dataset.csv     # Expanded feature dataset
│   └── tcad_results.csv          # Extracted TCAD results
│
├── results/
│   ├── confusion_matrix.png      # Classifier confusion matrix
│   ├── fault_distribution.png    # Fault-type distribution across bins
│   ├── coverage_vs_endurance.png # Coverage vs. endurance cycling
│   ├── coverage_errorbars.png    # Coverage with 95% CI error bars
│   ├── coverage_vs_pattern_count.png
│   ├── pattern_vs_coverage.png
│   └── vth_shift_vs_endurance.png
│
└── TCAD_WORKFLOW/
    ├── README.md                 # Workbench setup guide
    ├── fefet_sde.cmd             # SDE geometry script (Version A)
    ├── fefet_des.cmd             # SDevice physics script (Version A)
    ├── fefet_extract.tcl         # Inspect extraction (Version A)
    ├── memory_window/            # Version B: Program/Erase MW sweep
    │   ├── fefet_sde.cmd
    │   ├── fefet_des.cmd
    │   ├── README.md
    │   └── backup/               # Simplified fallback scripts
    └── backup/                   # Legacy MOSFET simulation cases
```

---

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Synopsys Sentaurus TCAD 2022.12** (for device simulation — optional if using pre-generated data)

### Installation

```bash
git clone https://github.com/aashishniranjanb/fefet-adaptive-testing.git
cd fefet-adaptive-testing
pip install -r requirements.txt
```

### Running the Pipeline

```bash
python run.py
```

This executes the full pipeline:
1. Generates a balanced dataset across 5 endurance bins (10³, 10⁴, 10⁵, 5×10⁵, 10⁶ cycles)
2. Labels each sample with the optimal test pattern
3. Trains a Random Forest classifier
4. Evaluates adaptive fault coverage vs. March C⁻ baseline
5. Produces all result plots in `results/`

### Running TCAD Simulations (Optional)

See [`TCAD_WORKFLOW/README.md`](TCAD_WORKFLOW/README.md) for Sentaurus Workbench setup instructions. Two simulation configurations are provided:

- **Version A** (`TCAD_WORKFLOW/`): Single gate sweep for basic V_th extraction
- **Version B** (`TCAD_WORKFLOW/memory_window/`): Full program/erase pulse sequence with memory window extraction

---

## Fault Models

The framework models five endurance-dependent fault types:

| Fault Type | Abbreviation | Physical Origin |
|---|---|---|
| Transition Fault | TF | Domain pinning prevents full polarization switching |
| Read Disturb Fault | RDF | Partial depolarization under read bias |
| Retention Fault | RF | Charge de-trapping causes state drift over time |
| State Coupling Fault | SCF | Inter-cell electrostatic coupling via trapped charge |
| Incorrect Read Fault | IRF | V_th shift pushes read margin below sense-amp threshold |

---

## TCAD Device Configuration

The Sentaurus Device simulation models a planar FeFET with:

- **Gate Stack**: TiN / HfO₂ (ferroelectric, 10 nm) / SiO₂ (buffer, 1 nm) / Si
- **Polarization Model**: Preisach hysteresis (P_s = 15 µC/cm², P_r = 12 µC/cm², E_c = 1.0 MV/cm)
- **Trap Models**: Acceptor traps at Si/SiO₂ interface + bulk traps in the ferroelectric layer
- **Sweep Parameters**: `@Nit@` (trap density), `@Temp@` (temperature in K)

---

## Toolchain

| Tool | Purpose |
|---|---|
| Synopsys Sentaurus TCAD | Device structure (SDE) and physics simulation (SDevice) |
| Python 3.8+ | Dataset generation, ML training, evaluation |
| scikit-learn | Random Forest classifier |
| NumPy / Pandas | Data processing |
| Matplotlib | Result visualization |

---

## License

This project is developed as part of academic research. Please contact the author for licensing inquiries.

## Author

**Aashish Niranjan B**
