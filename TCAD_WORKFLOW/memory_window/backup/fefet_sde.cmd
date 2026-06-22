;----------------------------------------------------------------------
; fefet_sde.cmd (Basic Backup Version)
; Sentaurus Structure Editor (SDE) script for a simplified planar structure.
; Geometry and mesh definition only.
;----------------------------------------------------------------------

(sde)
(sdegeo "ABA")

; ----------------------------
; Parameters (microns)
; ----------------------------
(define tSi 0.50) ; silicon body thickness
(define tOx 0.002) ; interfacial oxide thickness
(define tFe 0.010) ; HfO2 dielectric thickness
(define tGate 0.010) ; gate metal thickness

(define Ls 0.20) ; source length
(define Lg 0.60) ; gate length
(define Ld 0.20) ; drain length

(define Ltot (+ Ls Lg Ld))

; X-axis = vertical stack direction
(define XSiTop 0.0)
(define XSiBot tSi)
(define XOxTop (- XSiTop tOx))
(define XFeTop (- XOxTop tFe))
(define XGateTop (- XFeTop tGate))

; Y-axis = lateral direction
(define Ymin 0.0)
(define YsrcEnd Ls)
(define YgateStart Ls)
(define YgateEnd (+ Ls Lg))
(define YdrnStart (+ Ls Lg))
(define Ymax Ltot)

; ----------------------------
; Geometry
; ----------------------------

; Silicon substrate / body
(sdegeo
(position XSiTop Ymin 0)
(position XSiBot Ymax 0)
"Silicon" "region_Substrate"
)

; Source region
(sdegeo
(position XSiTop Ymin 0)
(position XSiBot YsrcEnd 0)
"Silicon" "region_Source"
)

; Drain region
(sdegeo
(position XSiTop YdrnStart 0)
(position XSiBot Ymax 0)
"Silicon" "region_Drain"
)

; Interfacial oxide under gate
(sdegeo
(position XOxTop YgateStart 0)
(position XSiTop YgateEnd 0)
"SiO2" "region_InterfacialOxide"
)

; Ferroelectric proxy layer (dielectric)
(sdegeo
(position XFeTop YgateStart 0)
(position XOxTop YgateEnd 0)
"HfO2" "region_Ferroelectric"
)

; Gate metal
(sdegeo
(position XGateTop YgateStart 0)
(position XFeTop YgateEnd 0)
"Metal" "region_GateMetal"
)

; ----------------------------
; Doping
; ----------------------------

(sdedr "dop_sub" "BoronActiveConcentration" 1e17)
(sdedr "place_sub" "dop_sub" "region_Substrate")

(sdedr "dop_src" "ArsenicActiveConcentration" 1e20)
(sdedr "place_src" "dop_src" "region_Source")

(sdedr "dop_drn" "ArsenicActiveConcentration" 1e20)
(sdedr "place_drn" "dop_drn" "region_Drain")

; ----------------------------
; Contacts (2D edges)
; ----------------------------

(sdegeo "Source" 4 (color 1 0 0) "##")
(sdegeo "Drain" 4 (color 0 1 0) "##")
(sdegeo "Gate" 4 (color 0 0 1) "##")
(sdegeo "Substrate" 4 (color 1 1 0) "##")

(sdegeo "Source")
(sdegeo
(list (car (find-edge-id (position XSiTop (/ YsrcEnd 2.0) 0))))
"Source"
)

(sdegeo "Drain")
(sdegeo
(list (car (find-edge-id (position XSiBot (+ YdrnStart (/ Ld 2.0)) 0))))
"Drain"
)

(sdegeo "Gate")
(sdegeo
(list (car (find-edge-id (position XGateTop (+ YgateStart (/ Lg 2.0)) 0))))
"Gate"
)

(sdegeo "Substrate")
(sdegeo
(list (car (find-edge-id (position XSiBot (/ Ymax 2.0) 0))))
"Substrate"
)

; ----------------------------
; Mesh refinement
; ----------------------------

; Global mesh
(sdedr "RefWin.Global" "Rectangle"
(position XGateTop Ymin 0)
(position XSiBot Ymax 0)
)
(sdedr "RefDef.Global" 0.05 0.05 0.02 0.02)
(sdedr "PlaceRF.Global" "RefDef.Global" "RefWin.Global")

; Gate/channel region
(sdedr "RefWin.Channel" "Rectangle"
(position XFeTop YgateStart 0)
(position 0.05 YgateEnd 0)
)
(sdedr "RefDef.Channel" 0.01 0.002 0.005 0.001)
(sdedr "PlaceRF.Channel" "RefDef.Channel" "RefWin.Channel")

; Left junction
(sdedr "RefWin.JunctionL" "Rectangle"
(position 0.0 0.0 0)
(position 0.15 (+ YsrcEnd 0.05) 0)
)
(sdedr "RefDef.Junction" 0.005 0.005 0.002 0.002)
(sdedr "PlaceRF.JunctionL" "RefDef.Junction" "RefWin.JunctionL")

; Right junction
(sdedr "RefWin.JunctionR" "Rectangle"
(position 0.0 (- YdrnStart 0.05) 0)
(position 0.15 Ymax 0)
)
(sdedr "PlaceRF.JunctionR" "RefDef.Junction" "RefWin.JunctionR")

; ----------------------------
; Build mesh
; ----------------------------
(sde "snmesh" "" "n@node@")
