from rocketcea.cea_obj import CEA_Obj


def get_combustion_properties(inputs):
    """
    Uses RocketCEA to compute combustion properties.
    Returns temperature, gamma and cstar.
    """

    Pc = inputs.chamber_pressure_bar * 14.5038

    cea = CEA_Obj(
        oxName=inputs.oxidizer,
        fuelName=inputs.fuel
    )

    Tc = cea.get_Tcomb(
        Pc=Pc,
        MR=inputs.mixture_ratio
    )

    mw, gamma = cea.get_Chamber_MolWt_gamma(
        Pc=Pc,
        MR=inputs.mixture_ratio
    )

    cstar = cea.get_Cstar(
        Pc=Pc,
        MR=inputs.mixture_ratio
    )

    return {
        "cea": cea,
        "Tc": Tc,
        "gamma": gamma,
        "cstar": cstar
    }