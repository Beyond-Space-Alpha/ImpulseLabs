<<<<<<< HEAD
import numpy as np


def chamber_length(rt, rc, L_star=1.0, conv_length=0.0):
    """
    Calculates the cylindrical chamber length for a rocket motor.
    
    Args:
        rt (float): Throat radius.
        rc (float): Chamber radius.
        L_star (float): Characteristic length (standard: L*).
        conv_length (float): Length of the converging nozzle section.
    """
    # Areas: Throat (At) and Chamber (Ac)
    At = np.pi * rt**2
    Ac = np.pi * rc**2

    # Volume of the converging section (frustum of a cone)
    V_conv = (np.pi * conv_length / 3.0) * (rc**2 + rc * rt + rt**2)

    # Total required combustion volume based on L_star
    V_total = L_star * At

    # Remaining volume required from the cylindrical section
    V_cyl = V_total - V_conv

    if V_cyl <= 0:
=======
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
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
        raise ValueError(
            "Converging section volume exceeds required total combustion volume. "
            "Increase L_star or reduce conv_length."
        )

<<<<<<< HEAD
    # Return L_cyl (Length of the cylindrical portion)
    return V_cyl / Ac
=======
    return v_cyl / Ac
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
