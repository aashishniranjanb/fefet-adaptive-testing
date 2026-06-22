import pandas as pd
import numpy as np
import os
from src.fault_models.fault_mapper import map_physics_to_fault
from src.simulation.labeling import get_best_test

def load_tcad_csv(path="data/tcad_results.csv"):
    if not os.path.exists(path):
        print(f"tcad_results.csv not found at {path}. Running extraction tool to generate it...")
        # Import vth_extract and run main to generate results
        import sys
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        import vth_extract
        vth_extract.main()
        
    df = pd.read_csv(path)
    return df

def expand_dataset(df, samples_per_point=600):
    dataset = []

    for _, row in df.iterrows():
        for _ in range(samples_per_point):
            # Add Gaussian variation to threshold voltages
            vth_ers_s = row["Vth_ers"] + np.random.normal(0, 0.02)
            vth_prg_s = row["Vth_prg"] + np.random.normal(0, 0.03)
            # Ensure Vth_prg is greater than Vth_ers
            if vth_prg_s < vth_ers_s + 0.1:
                vth_prg_s = vth_ers_s + 0.1
                
            mw_s = vth_prg_s - vth_ers_s
            
            # Add variation to currents
            ion_prg_s = row["Ion_prg"] * np.exp(np.random.normal(0, 0.05))
            ioff_prg_s = row["Ioff_prg"] * np.exp(np.random.normal(0, 0.1))
            
            temp_c = float(row.get("Temp_C", row.get("Temperature")))
            
            # Backward compatibility delta_vth mapping
            delta_vth = 0.05 + 0.15 * (1.20 - mw_s) / 0.70
            
            sample = {
                "memory_window": mw_s,
                "vth_ers": vth_ers_s,
                "vth_prg": vth_prg_s,
                "ion_prg": ion_prg_s,
                "ioff_prg": ioff_prg_s,
                "delta_vth": delta_vth,
                "Ncycles": int(row["Ncycles"]),
                "T": temp_c,
                "Nwrites": np.random.randint(10, 100)
            }

            dataset.append(sample)

    return dataset

def add_faults(dataset):
    for s in dataset:
        s["fault"] = map_physics_to_fault(
            s["memory_window"],
            s["vth_ers"],
            s["vth_prg"],
            s["ion_prg"],
            s["ioff_prg"],
            s["T"],
            s["Ncycles"],
            s["Nwrites"]
        )
    return dataset

def add_best_test(dataset):
    for s in dataset:
        s["best_test"] = get_best_test(s)
    return dataset

def build_dataset_from_tcad(path="data/tcad_results.csv"):
    df = load_tcad_csv(path)
    dataset = expand_dataset(df)
    dataset = add_faults(dataset)
    dataset = add_best_test(dataset)
    return dataset
