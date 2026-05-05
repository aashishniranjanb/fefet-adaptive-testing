import os
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

from src.dataset.generate import generate_dataset
from src.simulation.labeling import get_best_test
from src.simulation.fault_model import detect_fault, TESTS
from src.ml.train import prepare_data

# -----------------------------
# 1. Generate + Label Dataset
# -----------------------------
def build_dataset(n_samples=3000):
    dataset = generate_dataset(n_samples)

    for sample in dataset:
        sample["best_test"] = get_best_test(sample)

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

    # Confusion matrix
    cm = confusion_matrix(y_test, preds, labels=model.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
    
    plt.figure(figsize=(8, 6))
    disp.plot(cmap=plt.cm.Blues, ax=plt.gca())
    plt.title("ML Model Confusion Matrix")
    plt.savefig("results/confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()

    return model

# -----------------------------
# 3. Evaluate Coverage
# -----------------------------
def evaluate_coverage(dataset, model):
    results = {test: [] for test in TESTS}

    for sample in dataset:
        for test in TESTS:
            det = detect_fault(sample, test)
            results[test].append(det)

        # ML predicted test
        X = [[
            sample["delta_vth"],
            sample["Ncycles"],
            sample["T"],
            sample["Nwrites"]
        ]]
        pred_test = model.predict(X)[0]
        det_ml = detect_fault(sample, pred_test)
        results.setdefault("ML_Adaptive", []).append(det_ml)

    coverage = {
        k: 100 * np.mean(v) for k, v in results.items()
    }

    print("\n[Coverage Results]")
    for k, v in coverage.items():
        print(f"  {k}: {v:.2f}%")

    return coverage

# -----------------------------
# 4. Coverage vs Endurance Plot
# -----------------------------
def plot_coverage_vs_endurance(dataset, model):
    endurance_levels = [1e3, 1e4, 1e5]
    plot_data = {test: [] for test in TESTS + ["ML_Adaptive"]}

    for N in endurance_levels:
        subset = [d for d in dataset if d["Ncycles"] == N]
        if not subset:
            continue

        for test in TESTS:
            detections = [detect_fault(s, test) for s in subset]
            plot_data[test].append(100 * np.mean(detections))

        # ML adaptive
        detections = []
        for s in subset:
            X = [[s["delta_vth"], s["Ncycles"], s["T"], s["Nwrites"]]]
            pred = model.predict(X)[0]
            detections.append(detect_fault(s, pred))

        plot_data["ML_Adaptive"].append(100 * np.mean(detections))

    # Plot
    plt.figure(figsize=(8, 5))
    for k, v in plot_data.items():
        plt.plot([1, 2, 3], v, marker='o', linewidth=2, label=k)

    plt.xticks([1, 2, 3], ["1e3", "1e4", "1e5"])
    plt.xlabel("Endurance (cycles)")
    plt.ylabel("Fault Coverage (%)")
    plt.title("Fault Coverage vs. Endurance")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    os.makedirs("results", exist_ok=True)
    plt.savefig("results/coverage_vs_endurance.png", dpi=300, bbox_inches='tight')
    plt.close()

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
    dataset = build_dataset(3000)
    save_dataset(dataset)
    
    # Step 1b: Distribution Plot
    plot_fault_distribution(dataset)

    # Step 2: ML
    model = train_ml(dataset)

    # Step 3: Coverage
    coverage = evaluate_coverage(dataset, model)

    # Step 4: Plot
    plot_coverage_vs_endurance(dataset, model)

    print("\nPipeline complete. Check /results folder for plots!")

if __name__ == "__main__":
    main()
