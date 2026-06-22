*----------------------------------------------------------------------
* fefet_des.cmd (Basic Backup Version)
* Sentaurus Device (sdevice) script.
* Performs a simple gate voltage sweep (0 -> 2V) without complex 
* polarization hysteresis loops or traps to ensure absolute convergence.
*----------------------------------------------------------------------

Device FeFET {

  File {
    Grid = "n@node|fefet_sde@_msh.tdr"
    Plot = "n@node@_des.tdr"
    Current = "n@node@_des.plt"
    Output = "n@node@_des.log"
  }

  Electrode {
    { Name="Source" Voltage=0.0 }
    { Name="Drain" Voltage=0.05 }
    { Name="Gate" Voltage=0.0 WorkFunction=4.6 }
    { Name="Substrate" Voltage=0.0 }
  }

  Physics {
    Mobility( DopingDep )
    EffectiveIntrinsicDensity( OldSlotboom )
    Recombination( SRH )
  }

  Plot {
    eDensity hDensity
    eCurrent hCurrent
    ElectricField Potential SpaceCharge
    Doping DonorConcentration AcceptorConcentration
    eMobility hMobility
    eQuasiFermi hQuasiFermi
  }

  Math {
    Extrapolate
    RelErrControl
    Digits=6
    Iterations=25
    NotDamped=50
  }
}

System {
  FeFET f1 ( Source=s Drain=d Gate=g Substrate=b )

  Vsource_pset vs ( s 0 ) { dc = 0.0 }
  Vsource_pset vd ( d 0 ) { dc = 0.05 }
  Vsource_pset vg ( g 0 ) { dc = 0.0 }
  Vsource_pset vb ( b 0 ) { dc = 0.0 }
}

Solve {

  * Equilibrium solve
  NewCurrentPrefix="init_"
  Coupled { Poisson }
  Coupled { Poisson Electron Hole }

  * Simple Gate Sweep (0V to 2V)
  NewCurrentPrefix=""
  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=2.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }
}
