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
        raise ValueError(
            "Converging section volume exceeds required total combustion volume. "
            "Increase L_star or reduce conv_length."
        )

    # Return L_cyl (Length of the cylindrical portion)
    return V_cyl / Ac