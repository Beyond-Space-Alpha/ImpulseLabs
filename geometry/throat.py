import numpy as np


def throat_fillet(rt, radius=0.02, x0=0, n=40):

    theta = np.linspace(-np.pi/2, 0, n)

    x = x0 + radius * np.cos(theta)
    y = rt + radius * np.sin(theta)

    return list(zip(x, y))

