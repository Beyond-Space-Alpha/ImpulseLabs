"""Combustion properties solver using RocketCEA."""

from rocketcea.cea_obj import CEA_Obj

_BAR_TO_PSI = 14.5038   

def get_combustion_properties(inputs):

    """
    Uses RocketCEA to compute combustion properties.
     Note: Isp is NOT fetched here because it requires the expansion ratio,
    which is computed later in the performance module.
    Use get_isp_from_cea() once the expansion ratio is known.

    Parameters
    ----------
    inputs : EngineInputs

    Returns
    -------
     dict
        cea     : CEA_Obj   reusable instance for follow-up queries
        Tc      : float     adiabatic flame temperature [K]
        gamma   : float     ratio of specific heats at chamber conditions [-]
        cstar   : float     characteristic velocity [m/s]
        mw      : float     molecular weight of combustion products [kg/kmol]
        Pc_psi  : float     chamber pressure [psia] cached for reuse
    """

    Pc_psi = inputs.chamber_pressure_bar  * _BAR_TO_PSI

    cea = CEA_Obj(
        oxName=inputs.oxidizer,
        fuelName=inputs.fuel
    )

    Tc = cea.get_Tcomb(
        Pc=Pc_psi,
        MR=inputs.mixture_ratio
    )

    mw, gamma = cea.get_Chamber_MolWt_gamma(
        Pc=Pc_psi,
        MR=inputs.mixture_ratio
    )

    cstar = cea.get_Cstar(
        Pc=Pc_psi,
        MR=inputs.mixture_ratio
    )

    return {
        "cea": cea,
        "Tc": Tc,
        "gamma": gamma,
        "cstar": cstar,
        "mw": mw,
        "Pc_psi": Pc_psi
    }

def get_isp_from_cea(cea, Pc_psi, mixture_ratio, expansion_ratio):

    """
    Fetches specific impulse from a CEA_Obj instance for given conditions.
    Must be called AFTER the expansion ratio has been computed from the isentropic Mach solve in the performance module.
    Parameters
    ----------
    cea             : CEA_Obj   instance from get_combustion_properties()
    Pc_psi          : float     chamber pressure [psia]
    mixture_ratio   : float     O/F mass ratio [-]
    expansion_ratio : float     Ae/At [-]

    Returns
    -------
    Isp : float  specific impulse [s]
    """
    Isp = cea.get_Isp(
        Pc=Pc_psi, 
        MR=mixture_ratio, 
        eps=expansion_ratio
        )
    return float(Isp)