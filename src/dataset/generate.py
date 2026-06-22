import numpy as np
from src.fault_models.fault_mapper import map_physics_to_fault

def generate_sample():
    Ncycles = np.random.choice([1e3, 1e4, 1e5, 5e5, 1e6])
    T = np.random.choice([-40, 27, 85, 125])
    Nwrites = np.random.randint(10, 100)
    
    # Cycle index mapping
    cycle_indices = {1e3: 0, 1e4: 1, 1e5: 2, 5e5: 3, 1e6: 4}
    idx = cycle_indices[Ncycles]
    
    vth_ers_bases = [0.40, 0.45, 0.525, 0.65, 0.75]
    vth_prg_bases = [1.60, 1.55, 1.475, 1.35, 1.25]
    
    # Temperature in Kelvin
    temp_k = T + 273.15
    t_shift_ers = -0.0010 * (temp_k - 300.0)
    t_shift_prg = -0.0012 * (temp_k - 300.0)
    
    # Base extraction with Gaussian variation
    vth_ers = vth_ers_bases[idx] + t_shift_ers + np.random.normal(0, 0.02)
    vth_prg = vth_prg_bases[idx] + t_shift_prg + np.random.normal(0, 0.03)
    if vth_prg < vth_ers + 0.1:
        vth_prg = vth_ers + 0.1
        
    memory_window = vth_prg - vth_ers
    
    # Ion and Ioff with variation
    ion_prg = 1.0e-5 * ((300.0 / temp_k) ** 1.5) * np.exp(np.random.normal(0, 0.05))
    ioff_prg = 1.0e-13 * (temp_k / 300.0) * np.exp(np.random.normal(0, 0.10))
    
    # Backward compatibility delta_vth
    delta_vth = 0.05 + 0.15 * (1.20 - memory_window) / 0.70
    
    fault = map_physics_to_fault(
        memory_window, vth_ers, vth_prg, ion_prg, ioff_prg, T, Ncycles, Nwrites
    )
    
    return {
        "memory_window": memory_window,
        "vth_ers": vth_ers,
        "vth_prg": vth_prg,
        "ion_prg": ion_prg,
        "ioff_prg": ioff_prg,
        "delta_vth": delta_vth,
        "Ncycles": Ncycles,
        "T": T,
        "Nwrites": Nwrites,
        "fault": fault
    }

def assign_fault(delta_vth, T, Nwrites):
    """
    Deprecated: Keep for backward compatibility. Maps to map_physics_to_fault.
    """
    mw = 1.20 - ((delta_vth - 0.05) / 0.15) * 0.70
    if delta_vth > 0.18:
        ncycles = 1e6
    elif delta_vth > 0.12:
        ncycles = 1e5
    else:
        ncycles = 1e3
    return map_physics_to_fault(mw, 0.5, 0.5 + mw, 1e-5, 1e-13, T, ncycles, Nwrites)

def generate_dataset(n=3000):
    return [generate_sample() for _ in range(n)]
