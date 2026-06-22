;----------------------------------------------------------------------
; fefet_sde.cmd  (Version B — Memory Window / Program-Erase Sweep)
; Sentaurus Structure Editor (SDE) script for a planar FeFET.
; Geometry and mesh only.  Traps and Polarization are in SDEVICE.
;----------------------------------------------------------------------

; ----------------------------
; Parameters (microns)
; ----------------------------
(define tSi    0.50)   ; silicon body thickness
(define tOx    0.002)  ; interfacial oxide thickness (SiO2)
(define tFe    0.010)  ; ferroelectric layer thickness (HfO2/HZO)
(define tGate  0.010)  ; gate metal thickness (TiN)

(define Ls  0.20)      ; source extension length
(define Lg  0.60)      ; gate length
(define Ld  0.20)      ; drain extension length

(define Ltot (+ Ls Lg Ld))

; X-axis = vertical (stack) direction  —  gate on top, substrate below
(define XSiTop    0.0)
(define XSiBot    tSi)
(define XOxTop    (- XSiTop tOx))
(define XFeTop    (- XOxTop tFe))
(define XGateTop  (- XFeTop tGate))

; Y-axis = lateral direction
(define Ymin       0.0)
(define YsrcEnd    Ls)
(define YgateStart Ls)
(define YgateEnd   (+ Ls Lg))
(define YdrnStart  (+ Ls Lg))
(define Ymax       Ltot)

; ----------------------------
; Geometry  (2-D rectangles)
; ----------------------------

; Silicon substrate / body  (full width)
(sdegeo:create-rectangle
  (position XSiTop Ymin 0)
  (position XSiBot Ymax 0)
  "Silicon" "region_Substrate"
)

; Source region  (overwrites part of Substrate — same material)
(sdegeo:create-rectangle
  (position XSiTop Ymin 0)
  (position XSiBot YsrcEnd 0)
  "Silicon" "region_Source"
)

; Drain region
(sdegeo:create-rectangle
  (position XSiTop YdrnStart 0)
  (position XSiBot Ymax 0)
  "Silicon" "region_Drain"
)

; Interfacial oxide under gate
(sdegeo:create-rectangle
  (position XOxTop YgateStart 0)
  (position XSiTop YgateEnd  0)
  "SiO2" "region_InterfacialOxide"
)

; Ferroelectric layer (HfO2 proxy for HZO)
(sdegeo:create-rectangle
  (position XFeTop  YgateStart 0)
  (position XOxTop  YgateEnd   0)
  "HfO2" "region_Ferroelectric"
)

; Gate metal (TiN)
(sdegeo:create-rectangle
  (position XGateTop YgateStart 0)
  (position XFeTop   YgateEnd   0)
  "Metal" "region_GateMetal"
)

; ----------------------------
; Doping profiles
; ----------------------------

; p-type substrate  (uniform boron)
(sdedr:define-constant-profile "dop_sub"
  "BoronActiveConcentration" 1e17)
(sdedr:define-constant-profile-region "place_sub"
  "dop_sub" "region_Substrate")

; n+ source
(sdedr:define-constant-profile "dop_src"
  "ArsenicActiveConcentration" 1e20)
(sdedr:define-constant-profile-region "place_src"
  "dop_src" "region_Source")

; n+ drain
(sdedr:define-constant-profile "dop_drn"
  "ArsenicActiveConcentration" 1e20)
(sdedr:define-constant-profile-region "place_drn"
  "dop_drn" "region_Drain")

; ----------------------------
; Contacts  (2-D edge-based)
; ----------------------------

(sdegeo:define-contact-set "Source"    4 (color:rgb 1 0 0) "##")
(sdegeo:define-contact-set "Drain"     4 (color:rgb 0 1 0) "##")
(sdegeo:define-contact-set "Gate"      4 (color:rgb 0 0 1) "##")
(sdegeo:define-contact-set "Substrate" 4 (color:rgb 1 1 0) "##")

; Source contact — top edge of source region
(sdegeo:set-current-contact-set "Source")
(sdegeo:define-2d-contact
  (find-edge-id (position XSiTop (/ YsrcEnd 2.0) 0))
  "Source")

; Drain contact — bottom edge of drain region
(sdegeo:set-current-contact-set "Drain")
(sdegeo:define-2d-contact
  (find-edge-id (position XSiBot (+ YdrnStart (/ Ld 2.0)) 0))
  "Drain")

; Gate contact — top edge of gate metal
(sdegeo:set-current-contact-set "Gate")
(sdegeo:define-2d-contact
  (find-edge-id (position XGateTop (+ YgateStart (/ Lg 2.0)) 0))
  "Gate")

; Substrate contact — bottom edge of silicon
(sdegeo:set-current-contact-set "Substrate")
(sdegeo:define-2d-contact
  (find-edge-id (position XSiBot (/ Ymax 2.0) 0))
  "Substrate")

; ----------------------------
; Mesh refinement
; ----------------------------

; Global mesh
(sdedr:define-refinement-window "RefWin.Global" "Rectangle"
  (position XGateTop Ymin 0)
  (position XSiBot   Ymax 0))
(sdedr:define-refinement-size "RefDef.Global"
  0.05 0.05 0.02 0.02)
(sdedr:define-refinement-placement "PlaceRF.Global"
  "RefDef.Global" "RefWin.Global")

; Channel region  (fine mesh under the gate stack)
(sdedr:define-refinement-window "RefWin.Channel" "Rectangle"
  (position XFeTop YgateStart 0)
  (position 0.05   YgateEnd   0))
(sdedr:define-refinement-size "RefDef.Channel"
  0.01 0.002 0.005 0.001)
(sdedr:define-refinement-placement "PlaceRF.Channel"
  "RefDef.Channel" "RefWin.Channel")

; Left junction  (source-channel)
(sdedr:define-refinement-window "RefWin.JunctionL" "Rectangle"
  (position 0.0  0.0 0)
  (position 0.15 (+ YsrcEnd 0.05) 0))
(sdedr:define-refinement-size "RefDef.Junction"
  0.005 0.005 0.002 0.002)
(sdedr:define-refinement-placement "PlaceRF.JunctionL"
  "RefDef.Junction" "RefWin.JunctionL")

; Right junction  (drain-channel)
(sdedr:define-refinement-window "RefWin.JunctionR" "Rectangle"
  (position 0.0  (- YdrnStart 0.05) 0)
  (position 0.15 Ymax 0))
(sdedr:define-refinement-placement "PlaceRF.JunctionR"
  "RefDef.Junction" "RefWin.JunctionR")

; ----------------------------
; Build mesh
; ----------------------------
(sde:build-mesh "snmesh" "" "n@node@_msh")
