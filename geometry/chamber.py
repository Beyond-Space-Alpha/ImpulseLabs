# import numpy as np


# def chamber_length(rt, rc, L_star=1.0):

#     At = np.pi * rt**2
#     Ac = np.pi * rc**2

#     return L_star * At / Ac

import numpy as np


def chamber_length(rt, rc, L_star=1.0, conv_length=0.0):

    At = np.pi * rt**2
    Ac = np.pi * rc**2

    V_conv = (np.pi * conv_length / 3.0) * (rc**2 + rc * rt + rt**2)

    V_total = L_star * At

    V_cyl = V_total - V_conv

    if V_cyl <= 0:
        raise ValueError(
            "Converging section volume exceeds required total combustion volume. "
            "Increase L_star or reduce conv_length."
        )

    return V_cyl / Ac