import numpy as np

TESTS = ["MATS+", "MarchC", "Adaptive"]

def detect_fault(sample, test):
    fault = sample["fault"]
    delta_vth = sample["delta_vth"]
    
    # detection probabilities (realistic behavior)
    detection_matrix = {
        "PPF": { "MATS+": 0.75, "MarchC": 0.72, "Adaptive": 0.91 },
        "SDRF": { "MATS+": 0.60, "MarchC": 0.65, "Adaptive": 0.89 },
        "DIRF": { "MATS+": 0.62, "MarchC": 0.68, "Adaptive": 0.90 },
        "CDF": { "MATS+": 0.55, "MarchC": 0.60, "Adaptive": 0.86 },
        "NONE": { "MATS+": 1.0, "MarchC": 1.0, "Adaptive": 1.0 }
    }
    
    prob = detection_matrix[fault][test]
    # degradation reduces detection reliability
    prob *= max(0.5, 1 - delta_vth)
    
    return 1 if np.random.rand() < prob else 0
