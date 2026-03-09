import numpy as np


def chamber_geometry(rt, contraction_ratio):

    rc = rt * np.sqrt(contraction_ratio)

    return rc


def chamber_length(rt):

    L_star = 1.0

    return L_star * rt