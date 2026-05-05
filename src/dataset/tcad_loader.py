import pandas as pd
import numpy as np
import os

def load_tcad_data(path):
    if not os.path.exists(path):
        _generate_dummy_tcad(path)
        
    df = pd.read_csv(path)
    
    # compute raw delta
    df["delta_vth_raw"] = df["Vth_fresh"] - df["Vth_degraded"]
    
    return df

def normalize_delta_vth(df):
    """
    Map TCAD ΔVth → simulation range [0.05, 0.20]
    """
    min_v = df["delta_vth_raw"].min()
    max_v = df["delta_vth_raw"].max()
    
    # avoid divide-by-zero
    if max_v - min_v == 0:
        df["delta_vth"] = 0.1
        return df
        
    df["delta_vth"] = 0.08 + 0.22 * (
        (df["delta_vth_raw"] - min_v) / (max_v - min_v)
    )
    
    return df

def tcad_to_dataset(df):
    dataset = []
    
    from src.dataset.generate import assign_fault
    
    for _, row in df.iterrows():
        sample = {
            "delta_vth": row["delta_vth"],
            "Ncycles": int(row["Ncycles"]),
            "T": float(row["Temperature"]),
            "Nwrites": np.random.randint(10, 100)  # synthetic add-on
        }
        
        sample["fault"] = assign_fault(
            sample["delta_vth"], sample["T"], sample["Nwrites"]
        )
        
        dataset.append(sample)
        
    return dataset

def _generate_dummy_tcad(path):
    """Generates a realistic mock TCAD CSV for testing purposes."""
    print(f"Creating dummy TCAD data at {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    Ncycles = np.random.choice([1e3, 1e4, 1e5], 3000)
    T = np.random.choice([-40, 25, 125], 3000)
    
    # Vth fresh typically ~ 0.52V
    Vth_fresh = np.random.normal(0.52, 0.01, 3000)
    
    # Degraded Vth drops as cycles increase and temperature changes
    degradation = 0.01 * np.log10(Ncycles) + 0.0001 * T + np.random.normal(0, 0.002, 3000)
    Vth_degraded = Vth_fresh - degradation
    
    df = pd.DataFrame({
        "Ncycles": Ncycles,
        "Temperature": T,
        "Vth_fresh": Vth_fresh,
        "Vth_degraded": Vth_degraded
    })
    df.to_csv(path, index=False)
