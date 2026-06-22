# FeFET Sentaurus Workbench (SWB) Sweep Simulation Guide

This folder contains two versions of the Sentaurus TCAD configuration scripts for simulating and analyzing the FeFET memory cell under endurance degradation and temperature sweeps.

---

## 📂 File Versions Manifest

### Version A: Single Transfer Curve Sweep
Use this version to extract a single gate transfer curve sweep ($0\text{ V} \rightarrow 2\text{ V}$) for basic threshold voltage profiling:
*   **`fefet_sde.cmd`** – Sentaurus Structure Editor (SDE) input file. Builds the 2D planar transistor geometry.
*   **`fefet_des.cmd`** – Sentaurus Device (sdevice) input file. Solves the transfer sweep.
*   **`fefet_extract.tcl`** – Inspect/Tcl parameter extraction script. Extracts basic Vth.

### Version B: Memory Window Program/Erase Sweeps (Recommended)
Use this version to perform preconditioning program/erase pulse cycles before read sweeps, enabling true memory window hysteresis extraction:
*   **`fefet_sde_mw.cmd`** – SDE input file. Builds the planar transistor.
*   **`fefet_des_mw.cmd`** – SDevice input file. Runs the initial Poisson solve with line search damping, followed by program-pulse ($+2.5\text{ V} \rightarrow 0\text{ V}$), program-read ($0\text{ V} \rightarrow +2.0\text{ V}$), erase-pulse ($-2.5\text{ V} \rightarrow 0\text{ V}$), and erase-read ($0\text{ V} \rightarrow +2.0\text{ V}$) sweeps.
*   **`fefet_extract_mw.tcl`** – Inspect/Tcl script. Loads both program and erase curves, extracts $V_{th,prg}$ and $V_{th,ers}$, and computes $MW = V_{th,prg} - V_{th,ers}$.

---

## 🛠️ Sentaurus Workbench Project Setup

Follow these steps to wire and run the project inside the Sentaurus Workbench (SWB) GUI:

### Step 1: Create the Project and Add Tools
1. Open Sentaurus Workbench.
2. Select **File > New** to start a new project.
3. In the project flow diagram (bottom pane), add the following tools in this exact horizontal sequence:
   $$\text{SDE (sde)} \longrightarrow \text{SDEVICE (sdevice)} \longrightarrow \text{Inspect (inspect)}$$
4. Rename the tool labels if desired (e.g., `fefet_sde` / `fefet_sde_mw`, etc.).

### Step 2: Associate Input Files
Place the files from this directory into the project folder, then configure the tool inputs in SWB:
*   Right-click the **SDE node** > **Input Files > Add** > select the appropriate `.cmd` file (e.g., `fefet_sde_mw.cmd`).
*   Right-click the **SDEVICE node** > **Input Files > Add** > select the corresponding `.cmd` file (e.g., `fefet_des_mw.cmd`).
*   Right-click the **Inspect node** > **Input Files > Add** > select the corresponding Tcl extraction file (e.g., `fefet_extract_mw.tcl`).

### Step 3: Define Sweep Variables in SWB
You must declare the sweep variables in the project so SWB can parse the command templates:
1. In the SWB top menu, select **Project > Parameter Manager**.
2. Add the following parameters:
   *   **`Nit`** (Type: `float`) – Represents interface and bulk trap density ($cm^{-2}$).
   *   **`Temp`** (Type: `float`) – Represents operating temperature in Kelvin ($K$).
3. In the parameter values table, enter the sweep lists:
   *   `Nit` values: `1.00e10`, `1.78e10`, `2.34e10`, `3.16e10`, `4.73e10`
   *   `Temp` values: `233`, `300`, `358`, `398`
4. This creates a **5 × 4 sweep grid** (20 simulation nodes in total).

### Step 4: Add Extracted Output Variables
To expose the extracted metrics directly in the SWB variables table:
1. Open the Parameter Manager or Variables Table.
2. Add the corresponding results variables:
   *   For basic sweep: `Vth`
   *   For Memory Window sweep: `Vth_prg`, `Vth_ers`, and `MW`
3. The Tcl extraction scripts will automatically populate these variables upon completion using `set SWB_VARIABLES(var)`.

---

## ⚙️ Running the Simulations

1. Save the project (**File > Save**).
2. Right-click the root project node and select **Run > Run Selected Nodes** (or click the green **Run** toolbar icon).
3. The tools will execute in order. Once done, the nodes will turn **yellow** (done), and the variables table will be populated with the extracted values.

---

## 💡 Troubleshooting and Convergence Tips

*   **Instability / Divergence:**
    The first equilibrium solve can sometimes fail to converge due to polarization/charge boundary conditions. The memory-window script uses:
    `Coupled (LineSearchDamping=0.01, Iterations=100) { Poisson }`
    to stabilize. If convergence issues persist during bias ramps, reduce `InitialStep` to `0.001` in the SDevice script.
*   **Material Errors:**
    If your local Sentaurus installation database doesn't recognize HfO2, keep the region name `region_Ferroelectric` identical in SDE, but change the material field in SDE from `"HfO2"` to `"HfO2_highk"` or `"Oxide"`. Make sure the corresponding material name matches in the SDevice physics blocks.
