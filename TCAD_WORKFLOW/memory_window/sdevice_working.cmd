File {
  Grid = "@tdr@"
  Plot = "@tdrdat@"
  Current = "@plot@"
  Output = "@log@"
}

Electrode {
  { Name="Source"    Voltage=0.0 }
  { Name="Drain"     Voltage=0.0 }
  { Name="Gate"      Voltage=0.0 }
  { Name="Substrate" Voltage=0.0 }
}

Physics {
  Mobility( DopingDep HighFieldSaturation Enormal )
  EffectiveIntrinsicDensity( Slotboom )
  Recombination( SRH Auger )
}

Physics (RegionInterface="region_InterfacialOxide/region_Substrate") {
  Charge( Conc=1e12 ) 
}

Math {
  Extrapolate
  Derivatives
  RelErrControl
  Digits=5
  Method=ILS
  Iterations=20
  Notdamped=100
}

Solve {
  Coupled(Iterations=100){ Poisson }
  Coupled{ Poisson Electron Hole }
  
  Quasistationary(
     InitialStep=1e-3 Increment=1.35 MinStep=1e-5 MaxStep=0.05
     Goal{ Name="Drain" Voltage=0.05 }
  ){ Coupled{ Poisson Electron Hole } }
  
  Quasistationary(
     InitialStep=1e-3 Increment=1.35 MinStep=1e-5 MaxStep=0.05
     Goal{ Name="Gate" Voltage=1.5 }
  ){ Coupled{ Poisson Electron Hole } }
}
