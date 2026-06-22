# ------------------------------------------------------------
# fefet_extract.tcl
# Extract Vth_prg, Vth_ers, and Memory Window
# and push them into Sentaurus Workbench variables.
# ------------------------------------------------------------

# ---- Load program-state read curve ----
proj_load prg_read_n@node@_des.plt prg
cv_create prg_idvg "prg gate OuterVoltage" "prg drain TotalCurrent"
set Vth_prg [f_VT prg_idvg]

# ---- Load erase-state read curve ----
proj_load ers_read_n@node@_des.plt ers
cv_create ers_idvg "ers gate OuterVoltage" "ers drain TotalCurrent"
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
set fp [open "fefet_extracted.txt" "w"]
puts $fp "Vth_prg=$Vth_prg"
puts $fp "Vth_ers=$Vth_ers"
puts $fp "MW=$MW"
close $fp
