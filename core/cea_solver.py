"""Combustion properties solver using RocketCEA."""

from rocketcea.cea_obj import CEA_Obj

_BAR_TO_PSI = 14.5038
_FT_TO_M = 0.3048


def get_combustion_properties(inputs):
    """
    Uses RocketCEA to compute chamber combustion properties.

    Parameters
    ----------
    inputs : EngineInputs

    Returns
    -------
    dict
        cea     : CEA_Obj   reusable instance
        Tc      : float     adiabatic flame temperature [K]
        gamma   : float     ratio of specific heats at chamber conditions [-]
        cstar   : float     characteristic velocity [m/s]
        mw      : float     molecular weight [kg/kmol]
        Pc_psi  : float     chamber pressure [psia]
    """
    Pc_psi = inputs.chamber_pressure_bar * _BAR_TO_PSI

    cea = CEA_Obj(
        oxName=inputs.oxidizer,
        fuelName=inputs.fuel,
    )

    Tc_R = cea.get_Tcomb(
        Pc=Pc_psi,
        MR=inputs.mixture_ratio,
    )
    Tc_K = Tc_R * 5.0 / 9.0

    mw, gamma = cea.get_Chamber_MolWt_gamma(
        Pc=Pc_psi,
        MR=inputs.mixture_ratio,
    )

    cstar_ft_s = cea.get_Cstar(
        Pc=Pc_psi,
        MR=inputs.mixture_ratio,
    )
    cstar_m_s = cstar_ft_s * _FT_TO_M

    return {
        "cea": cea,
        "Tc": Tc_K,
        "gamma": gamma,
        "cstar": cstar_m_s,
        "mw": mw,
        "Pc_psi": Pc_psi,
    }


def get_cf_from_cea(cea, Pc_psi, mixture_ratio, expansion_ratio, ambient_pressure_bar):
    """
    Fetch thrust coefficient from RocketCEA for the solved nozzle condition.

    Parameters
    ----------
    cea : CEA_Obj
        RocketCEA object
    Pc_psi : float
        Chamber pressure [psia]
    mixture_ratio : float
        O/F ratio [-]
    expansion_ratio : float
        Area ratio Ae/At [-]
    ambient_pressure_bar : float
        Ambient pressure [bar]

    Returns
    -------
    float
        Thrust coefficient [-]
    """
    Pamb_psi = ambient_pressure_bar * _BAR_TO_PSI

    cf = cea.get_PambCf(
        Pc=Pc_psi,
        MR=mixture_ratio,
        eps=expansion_ratio,
        Pamb=Pamb_psi,
    )

    # Some RocketCEA installs return (Cf, mode) or similar.
    if isinstance(cf, tuple):
        cf = cf[0]

    return float(cf)