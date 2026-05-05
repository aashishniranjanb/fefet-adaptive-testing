import numpy as np

def generate_sample():
    Ncycles = np.random.choice([1e3, 1e4, 1e5])
    T = np.random.choice([-40, 25, 125])
    Nwrites = np.random.randint(1, 100)
    
    # degradation model with device variation & cycle-to-cycle noise
    device_variation = np.random.normal(0, 0.015)
    cycle_noise = np.random.normal(0, 0.005 * np.log10(Ncycles))
    
    delta_vth = 0.05 * np.log10(Ncycles) + 0.0005 * T + 0.0008 * Nwrites \
                + device_variation + cycle_noise
                
    # assign fault
    fault = assign_fault(delta_vth, T, Nwrites)
    
    return {
        "delta_vth": delta_vth,
        "Ncycles": Ncycles,
        "T": T,
        "Nwrites": Nwrites,
        "fault": fault
    }

def assign_fault(delta_vth, T, Nwrites):
    """ Fault labeling based on degradation physics """
    # Strong degradation → SDRF
    if delta_vth > 0.18 and T >= 25:
        return "SDRF"
    # Write instability → DIRF
    if delta_vth > 0.12 and Nwrites > 50:
        return "DIRF"
    # Moderate degradation → PPF
    if delta_vth > 0.07:
        return "PPF"
    # Coupling (rare, stochastic)
    if np.random.rand() < 0.1:
        return "CDF"
    return "NONE"

def generate_dataset(n=3000):
    return [generate_sample() for _ in range(n)]
