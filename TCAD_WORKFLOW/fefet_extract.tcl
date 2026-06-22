# ------------------------------------------------------------
# fefet_extract.tcl  (Version A — Single Gate Sweep)
# Extract a single Vth from the forward gate sweep and push
# the result into Sentaurus Workbench variables.
# ------------------------------------------------------------

# ---- Load the SDevice current plot file ----
# n@node|fefet_des@ resolves to the SDevice node number,
# so the filename becomes  n<N>_des.plt
proj_load n@node|fefet_des@_des.plt proj

# ---- Create Id-Vg curve from the default (unprefixed) dataset ----
cv_create idvg "proj gate OuterVoltage" "proj drain TotalCurrent"

# ---- Extract threshold voltage ----
set Vth [f_VT idvg]

# ---- Print to console ----
puts stdout "Vth = $Vth V"

# ---- Push value back to SWB variables table ----
set SWB_VARIABLES(Vth) $Vth

# ---- Optional: write a text file ----
set fp [open "fefet_extracted_vA.txt" "w"]
puts $fp "Vth=$Vth"
close $fp
