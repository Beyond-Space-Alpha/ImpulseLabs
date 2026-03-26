"""Combustion chamber length calculation."""

import numpy as np


def chamber_length(rt: float, rc: float, L_star: float = 1.0, conv_length: float = 0.0) -> float:
    """
    Compute cylindrical chamber length from characteristic length L*.

    Subtracts the frustum volume of the converging section from the
    total required combustion volume.

    Parameters
    ----------
    rt          : throat radius [m]
    rc          : chamber radius [m]
    L_star      : characteristic chamber length [m]
    conv_length : converging section axial length [m]

    Returns
    -------
    float : cylindrical chamber length [m]
    """
    At = np.pi * rt**2
    Ac = np.pi * rc**2

    v_conv = (np.pi * conv_length / 3.0) * (rc**2 + rc * rt + rt**2)
    v_total = L_star * At
    v_cyl = v_total - v_conv

    if v_cyl <= 0:
        raise ValueError(
            "Converging section volume exceeds required total combustion volume. "
            "Increase L_star or reduce conv_length."
        )

    return v_cyl / Ac