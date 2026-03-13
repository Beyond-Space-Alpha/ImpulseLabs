import numpy as np


def converging_parabola(rc, rt, x0, length, n=80):

    x = np.linspace(x0, x0 + length, n)

    s = (x - x0) / length

    y = rc - (rc - rt) * (s ** 2)

    return list(zip(x, y))

