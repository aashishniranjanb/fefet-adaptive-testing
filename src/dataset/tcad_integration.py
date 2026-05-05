import pandas as pd
import numpy as np
import os

def load_tcad_csv(path="data/tcad_results.csv"):
    if not os.path.exists(path):
        _generate_dummy_tcad_results(path)
        
    df = pd.read_csv(path)

    # reference = lowest degradation
    vth_ref = df["Vth"].max()

    # compute ΔVth
    df["delta_vth_raw"] = vth_ref - df["Vth"]

    return df

def normalize_delta_vth(df):
    min_v = df["delta_vth_raw"].min()
    max_v = df["delta_vth_raw"].max()

    # map to calibrated range [0.05 → 0.20]
    df["delta_vth"] = 0.05 + 0.18 * (
        (df["delta_vth_raw"] - min_v) / (max_v - min_v + 1e-9)
    )

    return df

def expand_dataset(df, samples_per_point=750):
    dataset = []

    for _, row in df.iterrows():
        for _ in range(samples_per_point):
            
            sample = {
                "delta_vth": row["delta_vth"] + np.random.normal(0, 0.005),
                "Ncycles": int(row["Ncycles"]),
                "T": float(row["Temperature"]),
                "Nwrites": np.random.randint(10, 100)
            }

            dataset.append(sample)

    return dataset

from src.dataset.generate import assign_fault

def add_faults(dataset):
    for s in dataset:
        s["fault"] = assign_fault(
            s["delta_vth"], s["T"], s["Nwrites"]
        )
    return dataset

from src.simulation.labeling import get_best_test

def add_best_test(dataset):
    for s in dataset:
        s["best_test"] = get_best_test(s)
    return dataset

def build_dataset_from_tcad(path="data/tcad_results.csv"):
    df = load_tcad_csv(path)
    df = normalize_delta_vth(df)

    dataset = expand_dataset(df)
    dataset = add_faults(dataset)
    dataset = add_best_test(dataset)

    return dataset

def _generate_dummy_tcad_results(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame([
        {"Ncycles": 1e3, "Temperature": 25, "Vth": 0.52},
        {"Ncycles": 1e4, "Temperature": 25, "Vth": 0.48},
        {"Ncycles": 1e5, "Temperature": 25, "Vth": 0.43},
        {"Ncycles": 1e5, "Temperature": 125, "Vth": 0.40}
    ])
    df.to_csv(path, index=False)
