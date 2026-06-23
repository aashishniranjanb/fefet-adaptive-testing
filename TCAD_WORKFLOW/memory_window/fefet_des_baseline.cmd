*----------------------------------------------------------------------
* fefet_des_baseline.cmd  -- BASELINE (Step 1 of 4)
* Goal: prove mesh + contacts + basic Id-Vg work. No traps, no polarization,
* no SWB parameters at all. If this fails, the problem is contacts/physics,
* not Nit/Temp.
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
  Fermi
  Mobility( DopingDep HighFieldSaturation Enormal )
  EffectiveIntrinsicDensity( OldSlotboom )
  Recombination( SRH )
}

Plot {
  eDensity hDensity
  Potential ElectricField
  eCurrent hCurrent
  eMobility hMobility
  Doping DonorConcentration AcceptorConcentration
}

Math {
  Extrapolate
  RelErrControl
  Digits=6
  Iterations=30
  NotDamped=50
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
* NEXT STEPS, ONE AT A TIME -- do not add more than one per run:
*
* STEP 2: add "Temperature = @Temp@" as the first line inside Physics{}.
*         Add the Temp parameter on this node (single value 300 first),
*         preprocess, run, confirm it still works.
*
* STEP 3: add back ONLY the interface-trap Physics(MaterialInterface=...)
*         block with Conc=@Nit@ (verify "Silicon/SiO2" is a real interface
*         in your structure first -- check Regions in Sentaurus Visual).
*         Add the Nit parameter, preprocess, run.
*
* STEP 4: add back the Polarization(Preisach(...)) block in
*         region_Ferroelectric. This is the most likely step to need
*         convergence tuning (smaller MaxStep, more Iterations) -- do it
*         last, once everything else is proven working.
*
* Do NOT reintroduce the System{}/Vsource_pset block. Direct Electrode +
* Goal{Name="..." Voltage=...} is simpler and is what this whole deck
* (and your program/erase pulses later) should use throughout.
* ----------------------------------------------------------------------
