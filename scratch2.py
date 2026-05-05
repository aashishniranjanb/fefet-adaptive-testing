import time

print("Starting loader...")
t0 = time.time()
from src.dataset.tcad_loader import load_tcad_data, normalize_delta_vth, tcad_to_dataset
print(f"Imports took {time.time()-t0:.2f}s")

t0 = time.time()
df = load_tcad_data("data/tcad_data.csv")
print(f"load_tcad_data took {time.time()-t0:.2f}s")

t0 = time.time()
df = normalize_delta_vth(df)
print(f"normalize_delta_vth took {time.time()-t0:.2f}s")

t0 = time.time()
dataset = tcad_to_dataset(df)
print(f"tcad_to_dataset took {time.time()-t0:.2f}s")

from src.simulation.labeling import get_best_test
t0 = time.time()
for s in dataset:
    s["best_test"] = get_best_test(s)
print(f"get_best_test loop took {time.time()-t0:.2f}s")
