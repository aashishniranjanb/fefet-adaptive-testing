# ------------------------------------------------------------
# fefet_extract.tcl  (Version B — Memory Window Extraction)
# Extract Vth_prg, Vth_ers, and Memory Window from the single
# .plt file produced by fefet_des.cmd.
#
# The SDevice deck writes all sweeps into one current file
# (n@node@_des.plt) using NewCurrentPrefix to tag datasets:
#   prg_read_  →  program-state transfer curve
#   ers_read_  →  erase-state transfer curve
# ------------------------------------------------------------

# ---- Load the single SDevice current plot file ----
proj_load n@node|fefet_des@_des.plt proj

# ---- Program-state Id-Vg curve ----
cv_create prg_idvg \
  "proj prg_read_gate OuterVoltage" \
  "proj prg_read_drain TotalCurrent"
set Vth_prg [f_VT prg_idvg]

# ---- Erase-state Id-Vg curve ----
cv_create ers_idvg \
  "proj ers_read_gate OuterVoltage" \
  "proj ers_read_drain TotalCurrent"
set Vth_ers [f_VT ers_idvg]

# ---- Compute memory window ----
set MW [expr {$Vth_prg - $Vth_ers}]

# ---- Print to console ----
puts stdout "Vth_prg = $Vth_prg V"
puts stdout "Vth_ers = $Vth_ers V"
puts stdout "MW      = $MW V"

# ---- Push values back to SWB variables table ----
set SWB_VARIABLES(Vth_prg) $Vth_prg
set SWB_VARIABLES(Vth_ers) $Vth_ers
set SWB_VARIABLES(MW)      $MW

# ---- Optional: write a text file ----
set fp [open "fefet_extracted_mw.txt" "w"]
puts $fp "Vth_prg=$Vth_prg"
puts $fp "Vth_ers=$Vth_ers"
puts $fp "MW=$MW"
close $fp
