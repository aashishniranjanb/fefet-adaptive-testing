# Basic Fallback Sentaurus Workbench Sweep Setup Guide

This folder contains a **basic, simplified MOSFET-like** sweep setup. If your complex FeFET sweep (with Preisach polarization, bulk traps, or program/erase pulses) fails to converge or compile in your Sentaurus lab environment, use this folder as a fallback to verify your device works.

---

## 🛠️ Step-by-Step SWB Walkthrough

### 1. Create the Project and Add Tool Nodes
1. Launch **Sentaurus Workbench** in your terminal (`swb &`).
2. Go to **Project > New > New Project** (Ctrl+N).
3. Right-click the **No Tools** placeholder in the tree flow pane $\rightarrow$ **Add**.
4. In the dialog:
   *   Tool: **Sentaurus Structure Editor** (Label: `fefet_sde`)
5. Right-click the `fefet_sde` node $\rightarrow$ **Add**:
   *   Tool: **Sentaurus Device** (Label: `fefet_des`)
6. Right-click the `fefet_des` node $\rightarrow$ **Add**:
   *   Tool: **Inspect** (Label: `fefet_extract`)

---

### 2. Paste Input Commands
1. Right-click **`fefet_sde`** $\rightarrow$ **Edit Input > Commands** (SEdit). Paste the contents of `fefet_sde.cmd`. Save.
2. Right-click **`fefet_des`** $\rightarrow$ **Edit Input > Commands**. Paste the contents of `fefet_des.cmd`. Save.
3. Right-click **`fefet_extract`** $\rightarrow$ **Edit Input > Commands**. Paste the contents of `fefet_extract.tcl`. Save.

---

### 3. Define Parameters
If you choose to run parameter sweeps, define the swept variables row under the **`fefet_des`** tool row:
*   **`Nit`** (Type: `float`): Enter your trap densities. (Note: In this basic backup, traps are disabled inside `fefet_des.cmd` to guarantee convergence, but you can add them back later).
*   **`Temp`**: Enter a list of temperature values (e.g. `300`).

---

### 4. Run the Project
1. Press **Ctrl+P** (Preprocess) to verify that placeholders substitution runs cleanly.
2. Press **Ctrl+R** (Run) to execute.
3. If successful (nodes turn yellow):
   - Double-click the `fefet_des` node to open in **Sentaurus Visual**.
   - Check if the $I_d-V_g$ curve successfully sweeps from $0.0\text{ V}$ to $2.0\text{ V}$.
   - The Inspect node will automatically extract the threshold voltage `Vth` and write it to `fefet_extracted.txt` and the SWB variables table.
