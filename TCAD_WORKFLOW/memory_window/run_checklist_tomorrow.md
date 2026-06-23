# Tomorrow's TCAD Run Checklist

> Read this first — one common mix-up

**Nit and Cycles are not independent.** Nit is the calibrated proxy for endurance — each cycle count maps to exactly one Nit value via `Nit = 1e10 * (Ncycles/1e3)^0.25` (already worked out in `swb_sweep_matrix.txt`). You don't pick any Nit with any cycle count.

What you actually choose freely is **Temperature**. So the real grid is:

```
5 fixed (Cycles, Nit) pairs  ×  4 Temp values  =  20 nodes
```

---

## Step 0 — One sanity node first (do this before the other 19)

In SWB, on the sdevice node:

1. Paste `fefet_des_main_grid.cmd` into the SDevice input
2. Set `Nit = 1.00e10` (single value)
3. Set `Temp = 300` (single value)
4. **Ctrl+P**, **Ctrl+R**
5. Confirm it converges and the Id-Vg curve looks sane (crosses 1e-7 A somewhere in a reasonable range, roughly near 0.5 V)

**Only after that passes, do Step 1.**

---

## Step 1 — Enter the full grid (2 lists, not 20 manual entries)

On the sdevice node, replace the single values with:

```
Nit  → 1.00e10, 1.78e10, 2.34e10, 3.16e10, 4.73e10
Temp → 233, 300, 358, 398
```

SWB automatically creates all 20 nodes (the cross product) the moment both lists are in. You do not set up each combination by hand.

---

## Step 2 — Ctrl+P, Ctrl+R, let it run

5–15 min per node → expect **2–5 hours total** for all 20.

---

## Step 3 — The actual 20 nodes, and what to export each one as

Press **Ctrl+2** then **F9** in SWB to see node number + parameter value together, so you can match each node to its row below. After each node finishes, export its Id-Vg curve as CSV (**Sentaurus Visual → File > Export**, or `svisual -csv IdVg_n<node#>_des.plt -o <filename below>`) and save it into `./tcad_raw/` under **exactly the filename in the last column** — `tcad_results_extract.py` depends on this exact naming.

| # | Cycles | Nit (cm⁻²) | Temp (K) | Temp (°C) | Export filename |
|---|--------|-----------|----------|-----------|-----------------|
| 1 | 1e3 | 1.00e10 | 233 | -40 | `results_Nit0_T0.csv` |
| 2 | 1e3 | 1.00e10 | 300 | 27 | `results_Nit0_T1.csv` |
| 3 | 1e3 | 1.00e10 | 358 | 85 | `results_Nit0_T2.csv` |
| 4 | 1e3 | 1.00e10 | 398 | 125 | `results_Nit0_T3.csv` |
| 5 | 1e4 | 1.78e10 | 233 | -40 | `results_Nit1_T0.csv` |
| 6 | 1e4 | 1.78e10 | 300 | 27 | `results_Nit1_T1.csv` |
| 7 | 1e4 | 1.78e10 | 358 | 85 | `results_Nit1_T2.csv` |
| 8 | 1e4 | 1.78e10 | 398 | 125 | `results_Nit1_T3.csv` |
| 9 | 3e4 | 2.34e10 | 233 | -40 | `results_Nit2_T0.csv` |
| 10 | 3e4 | 2.34e10 | 300 | 27 | `results_Nit2_T1.csv` |
| 11 | 3e4 | 2.34e10 | 358 | 85 | `results_Nit2_T2.csv` |
| 12 | 3e4 | 2.34e10 | 398 | 125 | `results_Nit2_T3.csv` |
| 13 | 1e5 | 3.16e10 | 233 | -40 | `results_Nit3_T0.csv` |
| 14 | 1e5 | 3.16e10 | 300 | 27 | `results_Nit3_T1.csv` |
| 15 | 1e5 | 3.16e10 | 358 | 85 | `results_Nit3_T2.csv` |
| 16 | 1e5 | 3.16e10 | 398 | 125 | `results_Nit3_T3.csv` |
| 17 | 5e5 | 4.73e10 | 233 | -40 | `results_Nit4_T0.csv` |
| 18 | 5e5 | 4.73e10 | 300 | 27 | `results_Nit4_T1.csv` |
| 19 | 5e5 | 4.73e10 | 358 | 85 | `results_Nit4_T2.csv` |
| 20 | 5e5 | 4.73e10 | 398 | 125 | `results_Nit4_T3.csv` |

---

## Step 4 — After all 20 CSVs are in `./tcad_raw/`

```bash
python3 tcad_results_extract.py
```

This produces:
- `tcad_processed/tcad_results.csv` — the backbone file (every Table/Figure cites this)
- `tcad_processed/fit_params.json` — the fitted degradation equation + R², RMSE
- `tcad_processed/fig_vth_vs_endurance.png` — your real Fig. 5

---

## NOT for tomorrow (do later, separately)

- ❌ Polarization / Preisach (2–4 bonus nodes only, after this grid is done)
- ❌ Cadence
- ❌ ML retraining (depends on `tcad_results.csv` existing first)
- ❌ Touching SDE (it's frozen)

---

## Key physics notes baked into the deck

1. **Donor traps** (not Acceptor) — produces Vth **decrease** with increasing Nit, matching your paper's Table I trend (0.52 → 0.40 V)
2. **`RegionInterface="region_Substrate/region_InterfacialOxide"`** — unambiguous; avoids the problem where `MaterialInterface="Silicon/SiO2"` could match Source or Drain regions too
3. **No `System{}`/`Vsource_pset`** — uses direct `Electrode` + `Goal{Name=...}` throughout
4. **`@tdr@`/`@plot@`/`@log@`** — SWB automatic file references, not hardcoded names
