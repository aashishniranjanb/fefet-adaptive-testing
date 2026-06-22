import numpy as np

def map_physics_to_fault(memory_window, vth_ers, vth_prg, ion_prg, ioff_prg, temp_c, ncycles, nwrites):
    """
    Physics-based mapping from FeFET device metrics to functional faults.
    
    Parameters:
    - memory_window: FeFET Memory Window (Vth_prg - Vth_ers)
    - vth_ers: Erase state threshold voltage (V)
    - vth_prg: Program state threshold voltage (V)
    - ion_prg: Program state ON current (A)
    - ioff_prg: Program state OFF current (A)
    - temp_c: Temperature in Celsius
    - ncycles: Number of endurance cycles (degradation state)
    - nwrites: Number of write cycles in the current operation/block
    
    Returns:
    - string: One of 'SDRF', 'PPF', 'DIRF', 'CDF'
    """
    
    # 1. SDRF (Sense Degradation Read Failure)
    # Sense amplifiers fail to distinguish state 0 and 1 if Memory Window is small (< 0.7 V)
    # Modeled via a sharp sigmoid curve.
    p_sdrf = 1.0 / (1.0 + np.exp((memory_window - 0.65) / 0.05))
    
    # 2. PPF (Program Failure)
    # Write switching failure due to domain pinning and high fatigue, exacerbated by low temperature
    p_ppf = 0.02
    if ncycles >= 1e5:
        p_ppf += 0.25 * (np.log10(ncycles) - 4.0)
    if temp_c < 0.0:
        p_ppf += 0.20 * (abs(temp_c) / 40.0)
    p_ppf = min(0.85, p_ppf)
        
    # 3. DIRF (Degradation-Induced Read Failure / Read Disturb)
    # Retention/read disturb under high write counts when window is degraded
    # High Nwrites increases trapped charge, triggering DIRF
    p_dirf = 0.40 * (nwrites / 100.0) * max(0.0, 1.25 - memory_window)
    p_dirf = min(0.80, p_dirf)
    
    # 4. CDF (Coupling Disturb Fault)
    # Electric field coupling from neighbor lines, worse at high temperature (low coercive field)
    # and high fatigue cycles
    p_cdf = 0.02
    if temp_c > 25.0:
        p_cdf += 0.25 * ((temp_c - 25.0) / 100.0) * (np.log10(ncycles) / 6.0)
    p_cdf = min(0.60, p_cdf)
    
    # Normalize probabilities to choose one of the 4 faults
    total = p_sdrf + p_ppf + p_dirf + p_cdf
    if total == 0:
        return "PPF"  # default fallback
        
    p_sdrf_n = p_sdrf / total
    p_ppf_n = p_ppf / total
    p_dirf_n = p_dirf / total
    p_cdf_n = p_cdf / total
    
    return np.random.choice(["SDRF", "PPF", "DIRF", "CDF"], p=[p_sdrf_n, p_ppf_n, p_dirf_n, p_cdf_n])
