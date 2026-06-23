*----------------------------------------------------------------------
* fefet_des_main_grid.cmd  -- THE deck for tomorrow's 20-node sweep
* (baseline + Temperature + interface traps. No polarization -- that's
*  a separate, later, 2-4 node bonus run, not part of this grid.)
*----------------------------------------------------------------------

File {
  Grid    = "@tdr@"
  Plot    = "@tdrdat@"
  Current = "@plot@"
  Output  = "@log@"
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
  Recombination( SRH )
}

* Endurance-degradation trap layer at the channel/gate-stack interface.
* This is the exact mechanism your own paper's Section III-A already
* names ("charge trapping, interface defect generation"), so this is
* the real degradation physics, not a placeholder.
*
* FIX vs the earlier draft: was "AcceptorTrap" (neutral -> NEGATIVE when
* it captures an electron), which would RAISE Vth as Nit grows -- the
* opposite of your paper's Table I trend (Vth falls 0.52 -> 0.40 V with
* degradation). "Donor" (neutral -> POSITIVE when it captures a hole) is
* the type that actually produces a Vth decrease, which is what you need
* to match your own published numbers.
*
* FIX vs the earlier draft: was "MaterialInterface=Silicon/SiO2" --
* "Silicon" is ambiguous (it's also region_Source and region_Drain).
* RegionInterface names the exact two regions, removing that ambiguity.
Physics( RegionInterface="region_Substrate/region_InterfacialOxide" ) {
  Traps(
    ( Donor Level
      EnergyMid = 0.56
      Conc      = @Nit@
      eXsection = 1e-15
      hXsection = 1e-15 )
  )
}

Plot {
  eDensity hDensity
  Potential ElectricField
  eCurrent hCurrent
  eMobility hMobility
  Doping DonorConcentration AcceptorConcentration
  eTrappedCharge hTrappedCharge
  eInterfaceTrappedCharge hInterfaceTrappedCharge
}

Math {
  Extrapolate
  RelErrControl
  Digits=6
  Iterations=30
  NotDamped=50
  Traps(Damping=100)
}

Solve {
  Coupled(Iterations=100) { Poisson }
  Coupled(Iterations=100) { Poisson Electron Hole }

  Quasistationary (
    InitialStep=0.01
    Increment=1.3
    MaxStep=0.05
    MinStep=1e-5
    Goal { Name="Gate" Voltage=2.0 }
  ) {
    Coupled { Poisson Electron Hole }
  }
}

* ----------------------------------------------------------------------
* BEFORE running all 20: set Nit to a single value (1.00e10) and Temp to
* a single value (300) first, preprocess, run that ONE node, confirm it
* still converges with traps added. Only then expand both parameters to
* their full 5-value / 4-value lists (see run_checklist_tomorrow.md) and
* run the rest.
* ----------------------------------------------------------------------
