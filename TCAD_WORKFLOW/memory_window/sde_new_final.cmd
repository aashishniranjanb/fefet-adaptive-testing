; ==========================================================================
; FeFET MFIS Structure Definition (Professional / Continuous Body Model)
; Architecture: Planar Metal-Ferroelectric-Insulator-Semiconductor
; Version: Final Frozen - Analytical Implants, Interface & Doping Refinements
; Units: Micrometers (um)
; ==========================================================================

; --------------------------------------------------------------------------
; 1. PARAMETER DEFINITIONS (Dimensions & Layers)
; --------------------------------------------------------------------------
(define t_Si    0.500)  ; Silicon Body: 500 nm
(define t_IL    0.002)  ; Interfacial Oxide (SiO2): 2 nm
(define t_FE    0.010)  ; Ferroelectric Layer (HfO2): 10 nm
(define t_Gate  0.020)  ; Gate Metal (TiN): 20 nm
(define xj      0.050)  ; Source/Drain Junction Depth: 50 nm

(define L_s     0.200)  ; Source Length: 200 nm
(define L_g     0.600)  ; Gate Length: 600 nm
(define L_d     0.200)  ; Drain Length: 200 nm
(define L_tot   (+ L_s L_g L_d))

; --------------------------------------------------------------------------
; 2. COORDINATE SYSTEM
; --------------------------------------------------------------------------
(define X_SiTop   0.0)
(define X_SiBot   t_Si)
(define X_OxTop   (- X_SiTop t_IL))
(define X_FeTop   (- X_OxTop t_FE))
(define X_GateTop (- X_FeTop t_Gate))

(define Y_min        0.0)
(define Y_srcEnd     L_s)
(define Y_gateStart  L_s)
(define Y_gateEnd    (+ L_s L_g))
(define Y_drnStart   (+ L_s L_g))
(define Y_max        L_tot)

; --------------------------------------------------------------------------
; 3. STRUCTURAL GEOMETRY (Single Continuous Substrate)
; --------------------------------------------------------------------------
; Single block of continuous Silicon (Removes artificial Si/Si interfaces)
(sdegeo:create-rectangle 
  (position X_SiTop Y_min 0) (position X_SiBot Y_max 0) 
  "Silicon" "region_Substrate")

; Interfacial Layer (IL)
(sdegeo:create-rectangle 
  (position X_OxTop Y_gateStart 0) (position X_SiTop Y_gateEnd 0) 
  "SiO2" "region_InterfacialOxide")

; Ferroelectric Layer
(sdegeo:create-rectangle 
  (position X_FeTop Y_gateStart 0) (position X_OxTop Y_gateEnd 0) 
  "HfO2" "region_Ferroelectric")

; Gate Metal (Updated to TiN for workfunction compatibility in SDevice)
(sdegeo:create-rectangle 
  (position X_GateTop Y_gateStart 0) (position X_FeTop Y_gateEnd 0) 
  "TiN" "region_GateMetal")

; --------------------------------------------------------------------------
; 4. DOPING PROFILES (Gaussian Implants via Ref/Eval Lines)
; --------------------------------------------------------------------------
; Baseline P-Substrate (1e17 cm-3)
(sdedr:define-constant-profile "dop_sub" "BoronActiveConcentration" 1e17)
(sdedr:define-constant-profile-region "place_sub" "dop_sub" "region_Substrate")

; Define Ref/Eval Lines at the Silicon surface for the implants
(sdedr:define-refeval-window "win_src_line" "Line" 
  (position X_SiTop Y_min 0) (position X_SiTop Y_srcEnd 0))
(sdedr:define-refeval-window "win_drn_line" "Line" 
  (position X_SiTop Y_drnStart 0) (position X_SiTop Y_max 0))

; Define a Gaussian analytical profile (Relative PeakPos = 0.0)
(sdedr:define-gaussian-profile "dop_gauss_n" "ArsenicActiveConcentration" 
  "PeakPos" 0.0 "PeakVal" 1e20 "ValueAtDepth" 1e17 "Depth" xj 
  "Gauss" "Factor" 0.8)

; Apply the analytical implants down into the Silicon (Positive direction)
(sdedr:define-analytical-profile-placement "place_src" "dop_gauss_n" "win_src_line" "Positive" "NoReplace" "Eval")
(sdedr:define-analytical-profile-placement "place_drn" "dop_gauss_n" "win_drn_line" "Positive" "NoReplace" "Eval")

; --------------------------------------------------------------------------
; 5. ELECTRICAL CONTACTS
; --------------------------------------------------------------------------
(sdegeo:define-contact-set "Source"    4 (color:rgb 1 0 0) "##")
(sdegeo:define-contact-set "Drain"     4 (color:rgb 0 1 0) "##")
(sdegeo:define-contact-set "Gate"      4 (color:rgb 0 0 1) "##")
(sdegeo:define-contact-set "Substrate" 4 (color:rgb 1 1 0) "##")

(sdegeo:set-current-contact-set "Source")
(sdegeo:set-contact (find-edge-id (position X_SiTop (/ Y_srcEnd 2.0) 0)) "Source")

(sdegeo:set-current-contact-set "Drain")
(sdegeo:set-contact (find-edge-id (position X_SiTop (+ Y_drnStart (/ L_d 2.0)) 0)) "Drain")

(sdegeo:set-current-contact-set "Gate")
(sdegeo:set-contact (find-edge-id (position X_GateTop (+ Y_gateStart (/ L_g 2.0)) 0)) "Gate")

(sdegeo:set-current-contact-set "Substrate")
(sdegeo:set-contact (find-edge-id (position X_SiBot (/ Y_max 2.0) 0)) "Substrate")

; --------------------------------------------------------------------------
; 6. MESH REFINEMENT (Global, Interface, and Doping-Gradient)
; --------------------------------------------------------------------------
; Global Mesh
(sdedr:define-refinement-window "RefWin.Global" "Rectangle"
  (position X_GateTop Y_min 0) (position X_SiBot Y_max 0))
(sdedr:define-refinement-size "RefDef.Global" 0.05 0.05 0.02 0.02)
(sdedr:define-refinement-placement "PlaceRF.Global" "RefDef.Global" "RefWin.Global")

; Channel & Stack Base Mesh
(sdedr:define-refinement-window "RefWin.Channel" "Rectangle"
  (position X_GateTop Y_gateStart 0) (position xj Y_gateEnd 0))
(sdedr:define-refinement-size "RefDef.Channel" 0.005 0.002 0.002 0.001)

; Advanced Interface Refinements (Crucial for trapping and electrostatic fields)
(sdedr:define-refinement-function "RefDef.Channel" "MaxLenInt" "Silicon" "SiO2" 0.0005 1.5 "DoubleSide")
(sdedr:define-refinement-function "RefDef.Channel" "MaxLenInt" "SiO2" "HfO2" 0.0005 1.5 "DoubleSide")
(sdedr:define-refinement-function "RefDef.Channel" "MaxLenInt" "HfO2" "TiN"  0.0005 1.5 "DoubleSide")

; Adaptive Doping Refinement (Automatically refines the grid at the P-N junctions)
(sdedr:define-refinement-function "RefDef.Channel" "DopingConcentration" "MaxTransDiff" 1)

(sdedr:define-refinement-placement "PlaceRF.Channel" "RefDef.Channel" "RefWin.Channel")

; --------------------------------------------------------------------------
; 7. MESH GENERATION (SWB Dynamic Output)
; --------------------------------------------------------------------------
(sde:build-mesh "snmesh" "" "n@node@_msh")
