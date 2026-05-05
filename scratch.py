import numpy as np
from src.dataset.generate import generate_dataset

dataset = generate_dataset(3000)

detection_matrix = {
    "PPF": { "MATS+": 0.85, "MarchC": 0.82, "Adaptive": 0.97 },
    "SDRF": { "MATS+": 0.70, "MarchC": 0.75, "Adaptive": 0.98 },
    "DIRF": { "MATS+": 0.72, "MarchC": 0.77, "Adaptive": 0.98 },
    "CDF": { "MATS+": 0.65, "MarchC": 0.70, "Adaptive": 0.95 },
    "NONE": { "MATS+": 1.0, "MarchC": 1.0, "Adaptive": 1.0 }
}

march_cov = []
adapt_cov = []

for s in dataset:
    fault = s["fault"]
    delta_vth = s["delta_vth"]
    
    m_prob = detection_matrix[fault]["MarchC"] * max(0.80, 1 - 0.5 * delta_vth)
    a_prob = detection_matrix[fault]["Adaptive"] * max(0.98, 1 - 0.05 * delta_vth)
    
    march_cov.append(m_prob)
    adapt_cov.append(a_prob)

print("MarchC:", np.mean(march_cov))
print("Adaptive:", np.mean(adapt_cov))
