go sdevice

File {
    Grid = "mos.tdr"
    Plot = "mos.plt"
    Current = "mos.cur"
    Output = "mos.log"
}

Electrode {
    { Name="gate"   Voltage=0 }
    { Name="drain"  Voltage=0.05 }
    { Name="source" Voltage=0 }
    { Name="bulk"   Voltage=0 }
}

Physics {
    Mobility
    SRH
    EffectiveIntrinsicDensity
    InterfaceTrap (Density=1e10)
}

Math {
    Extrapolate
    Iterations=30
}

Solve {

    # Sweep gate voltage → Id-Vg
    Quasistationary (
        InitialStep=0.01
        MaxStep=0.05
        Goal { Name="gate" Voltage=1.5 }
    ) {
        Coupled { Poisson Electron Hole }
    }

}
