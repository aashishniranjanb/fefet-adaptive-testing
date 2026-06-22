# click_by_click_swb_checklist.md

This checklist guides you click-by-click through setting up, de-risking, and running the FeFET Memory Window sweep inside **Sentaurus Workbench (SWB)** in the lab.

---

## 🧭 Step 0: Before You Launch SDB

Ensure the `STDB` (scratch/working directory) environment variable is set on your terminal before starting SWB:
```bash
export STDB=/path/to/your/scratch/directory
swb &
```

---

## 🛠️ Step 1: Tool Flow Construction

1. **Create Project:** Select **Project > New > New Project** (Ctrl+N) to open an empty workbench project.
2. **Add SDE Node:**
   - Right-click the **No Tools** placeholder in the tree view $\rightarrow$ **Add**.
   - Tool: **Sentaurus Structure Editor**
   - Label: `fefet_sde`
3. **Add SDEVICE Node:**
   - Right-click the `fefet_sde` node $\rightarrow$ **Add** (this links SDEVICE downstream).
   - Tool: **Sentaurus Device**
   - Label: `fefet_des`
4. **Add Inspect Node:**
   - Right-click the `fefet_des` node $\rightarrow$ **Add**.
   - Tool: **Inspect**
   - Label: `fefet_extract`

Your project toolbar flow should display:
$$\text{fefet\_sde} \longrightarrow \text{fefet\_des} \longrightarrow \text{fefet\_extract}$$

---

## 📝 Step 2: Input Commands Placement

1. Right-click **`fefet_sde`** $\rightarrow$ **Edit Input > Commands** (SEdit). Clear any placeholder content and paste the entire script from `fefet_sde.cmd`. Save.
2. Right-click **`fefet_des`** $\rightarrow$ **Edit Input > Commands**. Paste the entire script from `fefet_des.cmd`. Save.
3. Right-click **`fefet_extract`** $\rightarrow$ **Edit Input > Commands**. Paste the entire script from `fefet_extract.tcl`. Save.

---

## 📊 Step 3: Parametrizations

### Fixed parameters (single value)
If you wish to parameterize geometric or bias variables instead of using the default hardcoded values in SDE/SDevice, swap those variables with `@name@` placeholders and declare them under their respective tool rows:

| Parameter | Node | Recommended Value | Description |
| :--- | :--- | :--- | :--- |
| **`tSi`** | `fefet_sde` | `0.50` | Silicon body thickness ($\mu\text{m}$) |
| **`tOx`** | `fefet_sde` | `0.002` | Interfacial oxide thickness ($\mu\text{m}$) |
| **`tFe`** | `fefet_sde` | `0.010` | Ferroelectric layer thickness ($\mu\text{m}$) |
| **`Vd`** | `fefet_des` | `0.05` | Low drain bias to ensure linear Vth extraction |

*To add:* Right-click the gray parameter row under the relevant tool icon $\rightarrow$ **Add Parameter/Values** $\rightarrow$ enter name and value $\rightarrow$ Click **OK**.

### Swept parameters (multi-value list)
Right-click under **`fefet_des`** $\rightarrow$ **Add Parameter/Values** and declare the following sweeps:
*   **`Nit`**: `1.00e10, 1.78e10, 2.34e10, 3.16e10, 4.73e10`
*   **`Temp`**: `233, 300, 358, 398`

---

## 🔍 Step 4: De-risking via a Single Sanity-Check Node

Do not run the full 20-node sweep immediately. Instead, run a single test node first to confirm your model converges and yields expected results:

1. **Assign Single Test Values:**
   - Under `Nit`, input a single value: `1.00e10`
   - Under `Temp`, input a single value: `300`
2. **Preprocess:** Press **Ctrl+P** (Project > Operations > Preprocess) to verify that all `@...@` placeholders substitute without errors.
3. **Run Test Node:** Press **Ctrl+R** (Project > Operations > Run) and select the single node.
4. **Analyze Curve:**
   - Once the node turns **yellow** (successful), double-click to open in **Sentaurus Visual**.
   - Check if the $I_d-V_g$ curve successfully crosses the constant-current threshold ($I_{d,\text{crit}} = 10^{-7}\text{ A}$).
   - Verify that $V_{th}$ crosses near your target baseline (approx. $0.40 - 0.52\text{ V}$).
   - If convergence fails or $V_{th}$ is off, adjust your SDE dimensions/doping and rerun this single node.

---

## 🚀 Step 5: Full Sweep Execution

Once the sanity check converges cleanly:
1. Open the Parameter Manager and restore the full list of values under `Nit` and `Temp`.
2. SWB will automatically expand the project tree into the full 20-node cross-product.
3. Press **Ctrl+P** (Preprocess) and then **Ctrl+R** (Run) to queue the sweep.
4. Export the resulting `.plt` curves via the terminal:
   `svisual -csv prg_read_n<node#>_des.plt -o results_prg_Nit<i>_T<j>.csv`
   `svisual -csv ers_read_n<node#>_des.plt -o results_ers_Nit<i>_T<j>.csv`
5. Place these files in the `./tcad_raw/` folder and execute `python3 vth_extract.py` to fit the empirical model and generate the final tables!
