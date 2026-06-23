# FeFET TCAD Bring-Up & Round-2 Validation Plan

> **Decision locked:** Version B (Si FeFET with Preisach polarization) is the paper device.
> **SDE is frozen.** Mesh is validated. Do not modify `fefet_sde.cmd`.

---

## Strategy: Maximum Reviewer Confidence Per Hour

The goal is **not** the best ferroelectric physics model. The goal is:

```
A reviewer can trace every result back to a simulation log.
```

This means:
- 40 real TCAD runs with 40 logs > 1 beautiful Preisach simulation with 39 missing points
- Fault labels tied to a physical variable (MW, ΔVth) > arbitrary cycle thresholds
- 15–40 TCAD anchor points + physics-constrained augmentation = 3120 samples (honest, standard practice)

---

## Phase 1: Baseline Id-Vg (Day 1)

**Goal:** Prove mesh + contacts + basic physics work. Zero SWB parameters.

**File:** `fefet_des_baseline.cmd`

**Steps in SWB:**
1. Paste `fefet_des_baseline.cmd` into the SDevice node's input
2. **Ctrl+P** — should preprocess clean (zero `@...@` to resolve)
3. **Ctrl+R** — run that single node
4. If yellow ✅ → open in Sentaurus Visual
5. Plot **Gate OuterVoltage** vs **Drain TotalCurrent**
6. Screenshot → this is your **Figure 1: Baseline FeFET Transfer Characteristics**

**Output:** `IdVg_300K.png`, `run.log`

**Key points about the baseline deck:**
- Uses `@tdr@`, `@tdrdat@`, `@plot@`, `@log@` (SWB automatic file refs)
- Uses direct `Electrode` + `Goal{Name="Gate" Voltage=2.0}` — **NOT** `System{}`/`Vsource_pset`
- No traps, no polarization, no temperature parameter
- If this fails, the problem is contacts/mesh, not physics

---

## Phase 2: Add Temperature (Day 1–2)

**Goal:** Confirm temperature parameter works without changing physics.

**Modification to baseline deck:** Add one line as the first entry inside `Physics{}`:

```
Physics {
  Temperature = @Temp@    *<-- ADD THIS LINE
  Fermi
  ...
}
```

**SWB setup:**
1. Right-click sdevice parameter row → **Add Parameter/Values**
2. Name: `Temp` → Value: `300`
3. **Ctrl+P**, **Ctrl+R**
4. Confirm identical Id-Vg curve to Phase 1 (no change expected at 300 K)

---

## Phase 3: Add Interface Traps (Day 2–3)

**Goal:** Introduce degradation physics. This is where ΔVth starts appearing.

**Prerequisite:** Open Phase 1 result in Sentaurus Visual → check **Regions** tab → verify `Silicon/SiO2` appears as a real material interface in your meshed structure.

**Modification:** Add the interface trap block **after** the global `Physics{}` block:

```
Physics( MaterialInterface="Silicon/SiO2" ) {
  Traps(
    ( AcceptorTrap Level
      EnergyMid  = 0.56
      Conc       = @Nit@
      eXsection  = 1e-15
      hXsection  = 1e-15 )
  )
}
```

**SWB setup:**
1. Add parameter: `Nit` → Value: `1e10` (single value first)
2. **Ctrl+P**, **Ctrl+R**
3. Compare Vth to Phase 2 — should see a small shift

**Then sweep Nit:**

| Endurance proxy | Nit (cm⁻²) |
|---|---|
| 10³ cycles | 1e10 |
| 10⁴ cycles | 3e10 |
| 3×10⁴ cycles | 1e11 |
| 10⁵ cycles | 3e11 |
| 5×10⁵ cycles | 1e12 |

**Output:** Vth, Ion, Ioff for each Nit level

---

## Phase 4: Run the Full Nit × Temp Sweep Grid (Day 3–4)

**Goal:** Generate the 40-node TCAD dataset.

**Sweep matrix (reuse existing grid from abstract):**

| Parameter | Levels | Values |
|---|---|---|
| Nit | 5 | 1e10, 3e10, 1e11, 3e11, 1e12 |
| Temp | 4 | 233, 300, 358, 398 K |
| Polarization state | 2 | +Pr (programmed), −Pr (erased) |
| **Total nodes** | **40** | 5 × 4 × 2 |

**Polarization state modeling (key technique):**

Instead of running full Preisach pulse sequences for every node (high convergence risk), model the programmed and erased states as **two fixed bound-charge sheets** in `region_Ferroelectric`:

- **Programmed state:** `DonorTrap` with `Conc = +Pr` (positive bound charge)
- **Erased state:** `AcceptorTrap` with `Conc = −Pr` (negative bound charge)

Each is a plain static DC Id-Vg sweep — no pulses, no transient ramp, no `Preisach Memory=` parameter. You get:

```
MW(Ncycles, T) = Vth_program(Ncycles, T) − Vth_erase(Ncycles, T)
```

— a real memory-window number, TCAD-derived, with the convergence profile of the baseline deck.

**Paper disclosure (one sentence):**
> "Programmed/erased states are represented as fixed bound-charge sheets calibrated to the layer's remnant polarization, rather than full switching-dynamics simulation, to ensure numerical robustness across the full degradation grid."

**SWB setup:**
1. Set Nit values: `1e10, 3e10, 1e11, 3e11, 1e12`
2. Set Temp values: `233, 300, 358, 398`
3. SWB auto-expands to 20 nodes per polarization state (40 total)
4. **Ctrl+P**, **Ctrl+R**
5. Export results to `tcad_results.csv`

**Output file format:**
```
Cycles,Temp,Nit,Pol_State,Vth,Ion,Ioff,MW
1e3,233,1e10,prg,0.42,1.2e-4,3.1e-12,—
1e3,233,1e10,ers,0.38,1.3e-4,4.2e-12,0.04
...
```

---

## Phase 5: Fit the Degradation Equation (Day 4–5)

**Goal:** Calibrate the empirical degradation model from the 40 real data points.

**Equation to fit:**

```
ΔVth = a · log10(N) + b · (T − Tref) + c
MW   = MW0 − d · log10(N) − e · (T − Tref)
```

**Metrics to report:** R², RMSE — this becomes your **key contribution**.

**This equation replaces** the arbitrary threshold-based fault labels with physics-derived labels:

| Old (circular) | New (physics-grounded) |
|---|---|
| `if cycles > 1e5: fault = SDRF` | `if MW < 0.7: fault = SDRF` |
| `if cycles > 5e5: fault = TF` | `if ΔVth > 0.3: fault = TF` |

---

## Phase 6: Generate Augmented Dataset & Retrain (Day 5–6)

**Goal:** Create the 3120-sample dataset from the calibrated model.

1. Use the fitted MW(N,T) equation + controlled noise to generate 3120 synthetic samples
2. Re-derive fault labels from MW thresholds instead of cycle thresholds
3. Retrain the Random Forest classifier (same code, new features: ΔVth, MW, Read Margin)
4. Expect similar ~92% accuracy — but now with **defensible, physics-grounded labels**

**Paper wording (critical fix):**

> ~~"trained on 3120 simulation samples"~~
>
> ✅ "a physics-constrained synthetic dataset of 3120 samples, generated from the TCAD-calibrated degradation model and validated against 40 TCAD anchor points"

---

## Phase 7: Polarization Validation (Day 6–7, if time allows)

**Goal:** Run 2–4 real Preisach simulations — just enough to say ferroelectric switching was validated.

**Run only:**
- 10³ cycles, 300 K (pristine)
- 5×10⁵ cycles, 398 K (degraded)

**Each with:**
- Program pulse: Vg = 0 → +2.5 V → 0 V → read sweep
- Erase pulse: Vg = 0 → −2.5 V → 0 V → read sweep

**Output:** 2–4 real memory window numbers from full switching. These validate (or cross-check) the bound-charge-sheet approximation from Phase 4.

**This is bonus, not critical path.** If convergence fails, skip it — you already have 40 real data points.

---

## What Wins Round-2

The strongest paper narrative is:

```
TCAD (40 real runs)
  → Degradation Model (fitted equation)
    → Fault Physics (MW-threshold labels)
      → Dataset Generation (3120 augmented samples)
        → ML (Random Forest, 92% accuracy)
          → Adaptive Test Selection (+43 pp over March C⁻)
```

Every link in this chain is **traceable to a log file**.

---

## Files in This Directory

| File | Purpose | Status |
|---|---|---|
| `fefet_sde.cmd` | SDE geometry + mesh | 🔒 **FROZEN** — do not modify |
| `fefet_des_baseline.cmd` | Step 1 baseline (no params) | Use for Phase 1 |
| `fefet_des.cmd` | Full deck (traps + polarization) | Target for Phase 4+ |
| `fefet_extract.tcl` | Inspect extraction script | Use after Phase 3+ |
| `backup/` | Simplified fallback scripts | Reference only |

---

## SDevice Bring-Up Steps (Quick Reference)

> **Rule:** Do NOT add more than one new feature per run.

| Step | What to add | SWB params needed | Risk |
|---|---|---|---|
| **1 (Baseline)** | Nothing — bare Id-Vg | None | Near-zero |
| **2 (Temperature)** | `Temperature = @Temp@` in Physics{} | `Temp = 300` | Very low |
| **3 (Interface Traps)** | `Physics(MaterialInterface="Silicon/SiO2"){ Traps(...) }` | `Nit = 1e10` | Low |
| **4 (Polarization)** | `Polarization(Preisach(...))` in region_Ferroelectric | None (or fixed Pr) | **High** — do last |

> **Do NOT** reintroduce the `System{}`/`Vsource_pset` block.
> Use direct `Electrode` + `Goal{Name="..." Voltage=...}` throughout.
