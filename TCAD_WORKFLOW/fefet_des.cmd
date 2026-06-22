*----------------------------------------------------------------------
* fefet_des.cmd  (Version A — Single Gate Sweep)
* Sentaurus Device (sdevice) deck for a single Id-Vg transfer sweep
* on the FeFET structure built by fefet_sde.cmd.
*
* Extracts a single Vth from one forward gate sweep (0 → 2 V).
* For program/erase memory-window extraction, use memory_window/.
*
* SWB parameters:
*   @Nit@  = trap density (cm^-3 for bulk, cm^-2 for interface)
*   @Temp@ = temperature in Kelvin
*----------------------------------------------------------------------

Device FeFET {

  File {
    Grid    = "n@node|fefet_sde@_msh.tdr"
    Plot    = "n@node@_des.tdr"
    Current = "n@node@_des.plt"
    Output  = "n@node@_des.log"
  }

  Electrode {
    { Name="Source"    Voltage=0.0  }
    { Name="Drain"     Voltage=0.05 }
    { Name="Gate"      Voltage=0.0  WorkFunction=4.65 }
    { Name="Substrate" Voltage=0.0  }
  }

  Physics {
    Temperature = @Temp@

    Fermi
    Mobility( DopingDep HighFieldSaturation Enormal )
    EffectiveIntrinsicDensity( OldSlotboom )
    Recombination( SRH( DopingDependence ) )
  }

  * Ferroelectric polarization in the HfO2 / HZO region
  Physics( Region="region_Ferroelectric" ) {
    Polarization(
      Preisach(
        Ps  = 15e-6    * spontaneous polarization  [C/cm^2]
        Pr  = 12e-6    * remanent polarization     [C/cm^2]
        Ec  = 1.0e6    * coercive field             [V/cm]
      )
      Memory = 20
    )
    * Bulk trapping inside the ferroelectric layer
    Traps(
      ( AcceptorTrap Level
        EnergyMid  = 1.00
        Conc       = @Nit@
        eXsection  = 1e-15
        hXsection  = 1e-15 )
    )
  }

  * Interface traps at the Si / SiO2 boundary
  Physics( MaterialInterface="Silicon/SiO2" ) {
    Traps(
      ( AcceptorTrap Level
        EnergyMid  = 0.56
        Conc       = @Nit@
        eXsection  = 1e-15
        hXsection  = 1e-15 )
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
    Digits       = 6
    Iterations   = 25
    NotDamped    = 50
    Traps( Damping = 100 )
  }
}

System {
  FeFET f1 ( Source=s Drain=d Gate=g Substrate=b )

  Vsource_pset vs ( s 0 ) { dc = 0.0  }
  Vsource_pset vd ( d 0 ) { dc = 0.05 }
  Vsource_pset vg ( g 0 ) { dc = 0.0  }
  Vsource_pset vb ( b 0 ) { dc = 0.0  }
}

Solve {

  * Initial equilibrium
  NewCurrentPrefix = "init_"
  Coupled ( LineSearchDamping=0.01 Iterations=100 ) { Poisson }
  Coupled ( Iterations=100 ) { Poisson Electron Hole }

  * Single forward gate sweep:  0 V → 2 V
  NewCurrentPrefix = ""
  Quasistationary (
    InitialStep = 0.01
    MaxStep     = 0.05
    MinStep     = 1e-5
    Goal { Parameter=vg.dc  Value=2.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }
}
