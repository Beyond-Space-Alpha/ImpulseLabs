# import numpy as np


# def chamber_geometry(rt, contraction_ratio):

#     rc = rt * np.sqrt(contraction_ratio)

#     return rc


# def chamber_length(rt):

#     L_star = 1.0

#     return L_star * rt

import numpy as np

L_STAR_DEFAULT = 1.0   # meters


def chamber_geometry(rt, contraction_ratio):

    rc = rt * np.sqrt(contraction_ratio)

    return rc


def chamber_length(rt, contraction_ratio, L_star=L_STAR_DEFAULT):

    At = np.pi * rt**2

    Ac = contraction_ratio * At

    Vc = L_star * At

    Lc = Vc / Ac

    return Lc