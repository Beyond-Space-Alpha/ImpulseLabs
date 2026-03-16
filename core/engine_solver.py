import numpy as np
from core.validation import validate_inputs
from core.cea_solver import get_combustion_properties
from core.performance import (
    solve_exit_mach,
    expansion_ratio,
    mass_flow_rate,
    throat_area,
    diam_from_area,
)
from geometry.chamber import chamber_length


def solve_engine(inputs):
    """
    Full engine solution from validated inputs.
    Returns a dictionary that contains:
    -combustion properties
    -performance quantities
    -geometric quantities
    """

    validate_inputs(inputs)

    props = get_combustion_properties(inputs)

    gamma = props["gamma"]
    cstar = props["cstar"]

    # Temporary Isp estimate until a fuller performance model is added
    Isp = 250.0

    mdot = mass_flow_rate(inputs.thrust, Isp)

    Pc_pa = inputs.chamber_pressure_bar * 1e5

    At = throat_area(mdot, Pc_pa, cstar)
    dt = diam_from_area(At)
    rt = dt / 2.0

    Me = solve_exit_mach(
        gamma,
        inputs.chamber_pressure_bar,
        inputs.ambient_pressure_bar,
    )

    eps = expansion_ratio(Me, gamma)

    Ae = eps * At
    de = diam_from_area(Ae)
    re = de / 2.0

    rc = inputs.contraction_ratio * rt

    # Assuming a 40 degree converging angle for now, but this will be an input or optimization variable in the future
    theta_conv = np.radians(30.0)
    conv_length = (rc - rt) / np.tan(theta_conv)

    Lc = chamber_length(
        rt=rt,
        rc=rc,
        L_star=1.0,
        conv_length=conv_length,
    )

    return {
        "inputs": inputs,
        "cea": props["cea"],
        "Tc": props["Tc"],
        "gamma": gamma,
        "cstar": cstar,
        "Isp": Isp,
        "mdot": mdot,
        "Me": Me,
        "expansion_ratio": eps,
        "At": At,
        "Ae": Ae,
        "rt": rt,
        "re": re,
        "rc": rc,
        "Lc": Lc,
        "conv_length": conv_length,
    }