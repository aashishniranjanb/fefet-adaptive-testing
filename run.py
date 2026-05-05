import os
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import random

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

from src.dataset.generate import generate_dataset
from src.simulation.labeling import get_best_test
from src.simulation.fault_model import detect_fault, TESTS
from src.ml.train import prepare_data
from src.evaluation.stats import mean_ci_95_binary
from src.dataset.tcad_loader import load_tcad_data, normalize_delta_vth, tcad_to_dataset

# -----------------------------
# 1. Generate + Label Dataset
# -----------------------------
def build_dataset(samples_per_bin=1000):
    dataset = []
    # ensure balanced endurance bins
    for N in [1e3, 1e4, 1e5]:
        subset = generate_dataset(samples_per_bin)
        for s in subset:
            s["Ncycles"] = N
            s["best_test"] = get_best_test(s)
        dataset.extend(subset)
    return dataset

def build_dataset_from_tcad(path):
    df = load_tcad_data(path)
    df = normalize_delta_vth(df)
    dataset = tcad_to_dataset(df)

    for s in dataset:
        s["best_test"] = get_best_test(s)

    return dataset

# -----------------------------
# 1b. Data Distribution Plot
# -----------------------------
def plot_fault_distribution(dataset):
    faults = [d["fault"] for d in dataset]
    fault_counts = Counter(faults)
    
    print("\n[Dataset Realism - Fault Distribution]")
    for fault, count in fault_counts.items():
        print(f"  {fault}: {count} ({count/len(dataset)*100:.1f}%)")
        
    labels, values = zip(*fault_counts.items())
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974'][:len(labels)])
    plt.title("Fault Distribution in Dataset")
    plt.xlabel("Fault Type")
    plt.ylabel("Count")
    
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/fault_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------
# 2. Train ML Model
# -----------------------------
def train_ml(dataset):
    X, y = prepare_data(dataset)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"\n[ML] Accuracy: {acc:.3f}")

    cm = confusion_matrix(y_test, preds, labels=model.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
    
    plt.figure(figsize=(8, 6))
    disp.plot(cmap=plt.cm.Blues, ax=plt.gca())
    plt.title("ML Model Confusion Matrix")
    plt.savefig("results/confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()

    return model

def batch_ml_predict(model, dataset):
    X_all = [[s["delta_vth"], s["Ncycles"], s["T"], s["Nwrites"]] for s in dataset]
    all_preds = model.predict(X_all)
    preds = []
    for i, s in enumerate(dataset):
        if s["delta_vth"] > 0.12:
            preds.append("Adaptive")
        else:
            preds.append(all_preds[i])
    return preds

# -----------------------------
# 3. Coverage vs Endurance (with CI)
# -----------------------------
def plot_coverage_with_errorbars(dataset, model):
    levels = [1e3, 1e4, 1e5]
    x = np.log10(levels)

    march_mean, march_err = [], []
    adapt_mean, adapt_err = [], []

    for N in levels:
        subset = [d for d in dataset if d["Ncycles"] == N]
        if not subset:
            continue

        # March
        m = [detect_fault(s, "MarchC") for s in subset]
        mean, lo, hi = mean_ci_95_binary(m)
        march_mean.append(mean)
        march_err.append(mean - lo)

        # Adaptive
        a = []
        preds = batch_ml_predict(model, subset)
        for s, pred in zip(subset, preds):
            a.append(detect_fault(s, pred))

        mean, lo, hi = mean_ci_95_binary(a)
        adapt_mean.append(mean)
        adapt_err.append(mean - lo)

    plt.figure(figsize=(6, 4))
    plt.errorbar(x, march_mean, yerr=march_err, marker='o', linewidth=2, label="March C-")
    plt.errorbar(x, adapt_mean, yerr=adapt_err, marker='s', linewidth=2, label="Proposed Adaptive")

    plt.xticks(x, ["10³","10⁴","10⁵"])
    plt.xlabel("Endurance (Log Cycles)")
    plt.ylabel("Fault Coverage (%)")
    plt.title("Fault Coverage vs Endurance")
    plt.ylim(40, 100)
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.5)

    os.makedirs("results", exist_ok=True)
    plt.savefig("results/coverage_errorbars.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------
# 4. Coverage vs Pattern Count
# -----------------------------
def plot_coverage_vs_pattern_count(dataset, model):
    pattern_counts = [10, 20, 40, 60, 80, 100]
    march_cov = []
    adaptive_cov = []

    preds = batch_ml_predict(model, dataset)

    for p in pattern_counts:
        # March C- (less effective scaling)
        march_det = []
        march_trials = max(1, p // 25)
        for s in dataset:
            detections = [detect_fault(s, "MarchC") for _ in range(march_trials)]
            march_det.append(np.mean(detections))
        march_cov.append(100 * np.mean(march_det))

        # Adaptive (ML-based)
        adaptive_det = []
        adapt_trials = max(1, p // 12)
        for s, pred in zip(dataset, preds):
            detections = [detect_fault(s, pred) for _ in range(adapt_trials)]
            adaptive_det.append(np.mean(detections))

        adaptive_cov.append(100 * np.mean(adaptive_det))

    plt.figure(figsize=(6, 4))
    plt.plot(pattern_counts, march_cov, marker='o', linewidth=2, label="March C-")
    plt.plot(pattern_counts, adaptive_cov, marker='s', linewidth=2, label="Proposed Adaptive")

    plt.xlabel("Pattern Count")
    plt.ylabel("Fault Coverage (%)")
    plt.title("Coverage vs Pattern Count")
    plt.ylim(60, 100)
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend()

    os.makedirs("results", exist_ok=True)
    plt.savefig("results/coverage_vs_pattern_count.png", dpi=300, bbox_inches='tight')
    plt.close()

# -----------------------------
# TABLES WITH CI
# -----------------------------
def generate_table_1_with_ci(dataset, model):
    methods = ["MarchC", "Random", "ML_Adaptive"]
    print("\n=== TABLE I (with 95% CI) ===")
    print("Method\t\tCoverage (%) [95% CI]\tFNR (%)")

    preds = batch_ml_predict(model, dataset)

    for method in methods:
        dets = []
        for i, s in enumerate(dataset):
            if method == "MarchC":
                det = detect_fault(s, "MarchC")
            elif method == "Random":
                det = detect_fault(s, random.choice(["MATS+", "MarchC"]))
            else:
                det = detect_fault(s, preds[i])
            dets.append(det)

        mean, lo, hi = mean_ci_95_binary(dets)
        fnr = 100 - mean
        print(f"{method}\t\t{mean:.2f} [{lo:.2f}, {hi:.2f}]\t{fnr:.2f}")

def generate_table_2_with_ci(dataset, model):
    fault_types = ["PPF", "SDRF", "DIRF", "CDF"]
    print("\n=== TABLE II (with 95% CI) ===")
    print("Fault\tMarchC (%) [CI]\tAdaptive (%) [CI]")

    for f in fault_types:
        subset = [d for d in dataset if d["fault"] == f]
        if not subset:
            continue
        march = [detect_fault(s, "MarchC") for s in subset]
        adaptive = []
        preds = batch_ml_predict(model, subset)
        for s, pred in zip(subset, preds):
            adaptive.append(detect_fault(s, pred))

        m_mean, m_lo, m_hi = mean_ci_95_binary(march)
        a_mean, a_lo, a_hi = mean_ci_95_binary(adaptive)

        print(f"{f}\t{m_mean:.2f} [{m_lo:.2f},{m_hi:.2f}]\t{a_mean:.2f} [{a_lo:.2f},{a_hi:.2f}]")

def generate_ablation_with_ci(dataset, model):
    configs = ["Baseline", "Degradation_Model", "Adaptive"]
    print("\n=== TABLE III (Ablation with 95% CI) ===")
    print("Config\t\tCoverage (%) [CI]\tFNR (%)")

    preds = batch_ml_predict(model, dataset)

    for cfg in configs:
        dets = []
        for i, s in enumerate(dataset):
            if cfg == "Baseline":
                det = detect_fault(s, "MarchC")
            elif cfg == "Degradation_Model":
                test = "MATS+" if s["delta_vth"] > 0.12 else "MarchC"
                det = detect_fault(s, test)
            else:
                det = detect_fault(s, preds[i])
            dets.append(det)

        mean, lo, hi = mean_ci_95_binary(dets)
        fnr = 100 - mean
        print(f"{cfg}\t\t{mean:.2f} [{lo:.2f},{hi:.2f}]\t{fnr:.2f}")

# -----------------------------
# 5. Save Results
# -----------------------------
def save_dataset(dataset):
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)
            
    os.makedirs("data", exist_ok=True)
    with open("data/dataset.json", "w") as f:
        json.dump(dataset, f, indent=2, cls=NpEncoder)

# -----------------------------
# MAIN PIPELINE
# -----------------------------
def main():
    print("=== FeFET Adaptive Testing Pipeline ===")

    # Step 1: Dataset
    print("Building dataset...")
    dataset = build_dataset_from_tcad("data/tcad_data.csv")
    save_dataset(dataset)
    
    # Step 1b: Distribution Plot
    print("Plotting distribution...")
    plot_fault_distribution(dataset)

    # Step 2: ML
    print("Training ML...")
    model = train_ml(dataset)

    # Step 3: Plots
    print("Plotting coverage with error bars...")
    plot_coverage_with_errorbars(dataset, model)
    print("Plotting coverage vs pattern count...")
    plot_coverage_vs_pattern_count(dataset, model)

    # Step 4: Tables
    print("Generating Table I...")
    generate_table_1_with_ci(dataset, model)
    print("Generating Table II...")
    generate_table_2_with_ci(dataset, model)
    print("Generating Table III...")
    generate_ablation_with_ci(dataset, model)

    print("\nPipeline complete. Check /results folder for plots!")

if __name__ == "__main__":
    main()
