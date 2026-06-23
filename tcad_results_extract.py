"""
tcad_results_extract.py
----------------------------------------------------------------------
Builds the single backbone dataset for the paper:
    tcad_results.csv  -- columns: Cycles, Temp, Nit, Vth, Ion, Ioff

Every table and every fault-threshold in the paper should derive from
THIS file, and nothing else. If a number in the paper doesn't trace
back to a row here (or to the fitted model in fit_params.json), don't
publish it yet.

EXPECTED INPUT: a folder ./tcad_raw/ with one CSV per (Nit, T)
combination, named results_Nit<i>_T<j>.csv, columns GateVoltage,
DrainCurrent, exported from each sdevice node's Id-Vg sweep
(svisual -csv, or File > Export in Sentaurus Visual).

GRID (do not change without re-deriving the gamma fit in
swb_sweep_matrix.txt -- this is the already-calibrated grid):
    Nit_sweep_cm-2 = [1.00e10, 1.78e10, 2.34e10, 3.16e10, 4.73e10]
    Ncycles_labels = [1e3, 1e4, 3e4, 1e5, 5e5]
    Temp_sweep_K   = [233, 300, 358, 398]

USAGE:
    pip install numpy pandas scipy matplotlib
    python tcad_results_extract.py
----------------------------------------------------------------------
"""

import os
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# ---- Calibrated grid (locked -- do not change) ----
NCYCLES = np.array([1e3, 1e4, 3e4, 1e5, 5e5])
NIT     = np.array([1.00e10, 1.78e10, 2.34e10, 3.16e10, 4.73e10])  # cm^-2
TEMPS_K = np.array([233, 300, 358, 398])
TEMPS_C = np.array([-40, 27, 85, 125])

ID_CRIT = 1e-7  # A, constant-current Vth extraction threshold (W/L = 1)

RAW_DIR = "./tcad_raw"
OUT_DIR = "./tcad_processed"


def load_idvg(csv_path):
    """Load an Id-Vg CSV exported from Sentaurus Visual."""
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    vg_col = [c for c in df.columns if "gate" in c.lower() or c.lower() == "vg"][0]
    id_col = [c for c in df.columns if "current" in c.lower() or c.lower() == "id"][0]
    vg = df[vg_col].values.astype(float)
    idr = np.abs(df[id_col].values.astype(float))
    order = np.argsort(vg)
    return vg[order], idr[order]


def extract_vth_const_current(vg, idr, id_crit=ID_CRIT):
    """Vth via constant-current method: linear interpolation in log10(Id)."""
    log_id = np.log10(np.clip(idr, 1e-18, None))
    target = np.log10(id_crit)
    idx = np.where(log_id >= target)[0]
    if len(idx) == 0:
        return np.nan
    i1 = idx[0]
    if i1 == 0:
        return vg[0]
    i0 = i1 - 1
    frac = (target - log_id[i0]) / (log_id[i1] - log_id[i0])
    return vg[i0] + frac * (vg[i1] - vg[i0])


def extract_ion_ioff(vg, idr):
    """
    Ion  = drain current at the maximum swept Vg (full ON overdrive).
    Ioff = drain current at the minimum swept Vg (nominal OFF state).
    These feed the read-margin / Ion-Ioff-ratio side of the fault model,
    not just Vth -- needed so SDRF/DIRF thresholds can be defined on a
    physical read-margin quantity instead of an arbitrary cycle count.
    """
    ion = idr[np.argmax(vg)]
    ioff = idr[np.argmin(vg)]
    return ion, ioff


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    missing = []

    for i in range(len(NIT)):
        for j in range(len(TEMPS_K)):
            fname = f"results_Nit{i}_T{j}.csv"
            fpath = os.path.join(RAW_DIR, fname)
            if not os.path.exists(fpath):
                missing.append(fname)
                continue
            vg, idr = load_idvg(fpath)
            vth = extract_vth_const_current(vg, idr)
            ion, ioff = extract_ion_ioff(vg, idr)
            rows.append({
                "Cycles": NCYCLES[i],
                "Nit": NIT[i],
                "Temp": TEMPS_K[j],
                "Temp_C": TEMPS_C[j],
                "Vth": vth,
                "Ion": ion,
                "Ioff": ioff,
                "Ion_Ioff_ratio": (ion / ioff) if ioff > 0 else np.nan,
            })

    if missing:
        print(f"WARNING: {len(missing)} expected files not found, e.g. {missing[:3]}")
        print("These grid points have no log behind them -- do not fill them in by hand.")
        if not rows:
            print("ERROR: No data files found in ./tcad_raw/. Nothing to process.")
            return

    results = pd.DataFrame(rows)
    out_csv = os.path.join(OUT_DIR, "tcad_results.csv")
    results.to_csv(out_csv, index=False)
    print(f"\n=== tcad_results.csv ({len(results)} real TCAD-derived rows) ===")
    print(results.to_string(index=False))
    print(f"\nSaved {out_csv} -- this is the backbone file. Every Table/Figure")
    print("in the paper should cite a row in this file or the fit below, not a")
    print("number typed in separately.")

    # ---- Fit  Vth(Ncycles, Temp) = Vth0 - k_n*log10(N/1e3) - k_t*(T-300) ----
    X = (results["Cycles"].values, results["Temp"].values)
    y = results["Vth"].values
    valid = ~np.isnan(y)

    def model(Xdata, Vth0, k_n, k_t):
        ncycles, temp = Xdata
        return Vth0 - k_n * np.log10(ncycles / 1e3) - k_t * (temp - 300.0)

    try:
        popt, pcov = curve_fit(model, (X[0][valid], X[1][valid]), y[valid],
                                p0=[0.55, 0.03, 0.0008], maxfev=10000)
        Vth0, k_n, k_t = popt
        perr = np.sqrt(np.diag(pcov))
        residuals = y[valid] - model((X[0][valid], X[1][valid]), *popt)
        rmse = np.sqrt(np.mean(residuals**2))
        r2 = 1 - np.sum(residuals**2) / np.sum((y[valid] - np.mean(y[valid]))**2)

        print("\n=== Fitted degradation model (real anchor points only) ===")
        print(f"Vth(Ncycles, T) = {Vth0:.4f} - {k_n:.4f}*log10(Ncycles/1e3) "
              f"- {k_t:.6f}*(T - 300)")
        print(f"Std errors: Vth0={perr[0]:.4f}, k_n={perr[1]:.4f}, k_t={perr[2]:.6f}")
        print(f"Fit quality: RMSE={rmse:.5f} V, R^2={r2:.4f}  (report both in the paper)")

        fit_json = os.path.join(OUT_DIR, "fit_params.json")
        with open(fit_json, "w") as f:
            json.dump({
                "Vth0": Vth0, "k_n": k_n, "k_t": k_t, "t_ref": 300.0,
                "rmse_V": rmse, "r2": r2, "n_anchor_points": int(valid.sum()),
                "model": "Vth = Vth0 - k_n*log10(Ncycles/1e3) - k_t*(T-300)"
            }, f, indent=2)
        print(f"\nSaved {fit_json}. n_anchor_points is the honest number to "
              "cite when you describe how the synthetic dataset was generated -- "
              "e.g. '3120 physics-constrained samples generated from a degradation "
              f"model calibrated against {int(valid.sum())} TCAD anchor points.'")
    except Exception as e:
        print(f"Fit failed (likely too few valid points): {e}")
        return

    # ---- Plot: Vth vs Endurance, one line per temperature ----
    fig, ax = plt.subplots(figsize=(6, 4))
    for j, t in enumerate(TEMPS_K):
        sub = results[results["Temp"] == t]
        if len(sub):
            ax.plot(sub["Cycles"], sub["Vth"], marker="o",
                    label=f"T = {TEMPS_C[j]}°C")
    ax.set_xscale("log")
    ax.set_xlabel("Endurance Cycles")
    ax.set_ylabel("Threshold Voltage Vth (V)")
    ax.set_title("TCAD-Extracted Vth vs Endurance (real anchor points)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig_path = os.path.join(OUT_DIR, "fig_vth_vs_endurance.png")
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)
    print(f"\nSaved {fig_path}")

    # ---- Plot: Ion/Ioff ratio vs Endurance ----
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for j, t in enumerate(TEMPS_K):
        sub = results[results["Temp"] == t]
        if len(sub):
            ax2.plot(sub["Cycles"], sub["Ion_Ioff_ratio"], marker="s",
                     label=f"T = {TEMPS_C[j]}°C")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Endurance Cycles")
    ax2.set_ylabel("Ion / Ioff Ratio")
    ax2.set_title("TCAD-Extracted Ion/Ioff vs Endurance")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    fig2_path = os.path.join(OUT_DIR, "fig_ion_ioff_vs_endurance.png")
    fig2.savefig(fig2_path, dpi=150)
    plt.close(fig2)
    print(f"Saved {fig2_path}")


if __name__ == "__main__":
    main()
