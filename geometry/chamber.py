import numpy as np


def chamber_length(rt, rc, L_star=1.0):

    At = np.pi * rt**2
    Ac = np.pi * rc**2

    return L_star * At / Ac