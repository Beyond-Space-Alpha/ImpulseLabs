from rocketcea.cea_obj import CEA_Obj


def get_combustion_properties(inputs):
    """
    Uses RocketCEA to compute combustion properties.
    Returns temperature, gamma and cstar.
    """

    # PEP 8: Use snake_case for variables (pc instead of Pc)
    pc_psi = inputs.chamber_pressure_bar * 14.5038

    cea = CEA_Obj(
        oxName=inputs.oxidizer,
        fuelName=inputs.fuel
    )

    tc = cea.get_Tcomb(
        Pc=pc_psi,
        MR=inputs.mixture_ratio
    )

    mw, gamma = cea.get_Chamber_MolWt_gamma(
        Pc=pc_psi,
        MR=inputs.mixture_ratio
    )

    cstar = cea.get_Cstar(
        Pc=pc_psi,
        MR=inputs.mixture_ratio
    )

    return {
        "cea": cea,
        "Tc": tc,
        "gamma": gamma,
        "cstar": cstar
    }