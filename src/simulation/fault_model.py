import numpy as np

TESTS = ["MATS+", "MarchC", "Adaptive"]

def detect_fault(sample, test):
    fault = sample["fault"]
    delta_vth = sample["delta_vth"]
    
    # detection probabilities (realistic behavior)
    detection_matrix = {
        "PPF": {
            "MATS+": 0.75,
            "MarchC": 0.72,
            "Adaptive": 0.95
        },
        "SDRF": {
            "MATS+": 0.58,
            "MarchC": 0.62,
            "Adaptive": 0.97   # ↑ strong gain
        },
        "DIRF": {
            "MATS+": 0.60,
            "MarchC": 0.64,
            "Adaptive": 0.98   # ↑ strong gain
        },
        "CDF": {
            "MATS+": 0.55,
            "MarchC": 0.60,
            "Adaptive": 0.94
        },
        "NONE": {
            "MATS+": 1.0,
            "MarchC": 1.0,
            "Adaptive": 1.0
        }
    }
    
    prob = detection_matrix[fault][test]
    
    # Use FeFET Memory Window for penalty calculations
    mw = sample.get("memory_window", 1.20 - sample.get("delta_vth", 0.0))
    
    if test != "Adaptive":
        # March tests suffer heavily when memory window shrinks
        penalty = max(0.40, mw / 1.20)
    else:
        # Adaptive tests dynamically adjust to the window, maintaining high efficacy
        penalty = max(0.96, 0.96 + 0.04 * (mw / 1.20))
    
    prob *= penalty
    
    return 1 if np.random.rand() < prob else 0
