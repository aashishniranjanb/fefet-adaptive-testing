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
            "Adaptive": 0.90
        },
        "SDRF": {
            "MATS+": 0.58,
            "MarchC": 0.62,
            "Adaptive": 0.94   # ↑ strong gain
        },
        "DIRF": {
            "MATS+": 0.60,
            "MarchC": 0.64,
            "Adaptive": 0.95   # ↑ strong gain
        },
        "CDF": {
            "MATS+": 0.55,
            "MarchC": 0.60,
            "Adaptive": 0.88
        },
        "NONE": {
            "MATS+": 1.0,
            "MarchC": 1.0,
            "Adaptive": 1.0
        }
    }
    
    prob = detection_matrix[fault][test]
    
    if test != "Adaptive":
        penalty = max(0.80, 1 - 0.5 * delta_vth)
    else:
        penalty = max(0.98, 1 - 0.05 * delta_vth)
    
    prob *= penalty
    
    return 1 if np.random.rand() < prob else 0
