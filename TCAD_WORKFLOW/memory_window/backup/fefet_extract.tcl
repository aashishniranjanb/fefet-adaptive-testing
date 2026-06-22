# ------------------------------------------------------------
# fefet_extract.tcl  (Basic Backup Version)
# Extract Vth from a single transfer-curve sweep and push to SWB.
# ------------------------------------------------------------

# ---- Load the SDevice current plot file ----
proj_load n@node|fefet_des@_des.plt proj

# ---- Create Id-Vg curve ----
cv_create idvg "proj gate OuterVoltage" "proj drain TotalCurrent"
set Vth [f_VT idvg]

# ---- Print to console ----
puts stdout "Vth = $Vth V"

# ---- Push value back to SWB variables table ----
set SWB_VARIABLES(Vth) $Vth

# ---- Optional: write a text file ----
set fp [open "fefet_extracted.txt" "w"]
puts $fp "Vth=$Vth"
close $fp
