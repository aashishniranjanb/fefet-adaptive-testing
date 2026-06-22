*----------------------------------------------------------------------
* fefet_des.cmd
* Sentaurus Device (sdevice) deck for FeFET program/erase/read sweeps.
*
* Project parameters:
*   @Nit@  = trap density sweep value
*   @Temp@ = temperature in Kelvin
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
    Temperature = @Temp@

    Fermi
    Mobility( DopingDep HighFieldSaturation Enormal )
    EffectiveIntrinsicDensity( OldSlotboom )
    Recombination( SRH( DopingDependence ) )
  }

  * Ferroelectric polarization in the HfO2 / HZO proxy region
  Physics( Region="region_Ferroelectric" ) {
    Polarization( Memory=20 )
    * Optional bulk trapping inside the ferroelectric proxy layer
    Traps(
      ( AcceptorTrap Level
        EnergyMid=1.00
        Conc=@Nit@
        eXsection=1e-15
        hXsection=1e-15 )
    )
  }

  * Interface traps at the Si / SiO2 boundary
  Physics( MaterialInterface="Silicon/SiO2" ) {
    Traps(
      ( AcceptorTrap Level
        EnergyMid=0.56
        Conc=@Nit@
        eXsection=1e-15
        hXsection=1e-15 )
    )
  }

  Plot {
    eDensity hDensity
    eCurrent hCurrent
    ElectricField Potential SpaceCharge
    Doping DonorConcentration AcceptorConcentration
    eMobility hMobility
    eQuasiFermi hQuasiFermi
    Polarization/Vector
    eTrappedCharge hTrappedCharge
    eInterfaceTrappedCharge hInterfaceTrappedCharge
  }

  Math {
    Extrapolate
    RelErrControl
    Digits=6
    Iterations=25
    NotDamped=50
    Traps(Damping=100)
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

  * Initial equilibrium
  NewCurrentPrefix="init_"
  Coupled (LineSearchDamping=0.01, Iterations=100) { Poisson }
  Coupled (Iterations=100) { Poisson Electron Hole }

  * PROGRAM STATE
  * Drive gate positive, return to 0, then perform read sweep
  NewCurrentPrefix="prg_pulse_"
  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=2.5 }
  ) {
    Coupled { Poisson Electron Hole }
  }

  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=0.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }

  NewCurrentPrefix="prg_read_"
  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=2.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }

  * ERASE STATE
  * Drive gate negative, return to 0, then perform read sweep
  NewCurrentPrefix="ers_pulse_"
  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=-2.5 }
  ) {
    Coupled { Poisson Electron Hole }
  }

  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=0.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }

  NewCurrentPrefix="ers_read_"
  Quasistationary (
    InitialStep=0.01
    MaxStep=0.05
    MinStep=1e-5
    Goal { Parameter=vg.dc Value=2.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }
}
