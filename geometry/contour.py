import numpy as np


def generate_contour(rt, re, length, n=200):

    x = np.linspace(0, length, n)

    y = rt + (re - rt) * (x / length) ** 2

    contour = list(zip(x, y))

    return contour