# import numpy as np


# def generate_contour(rt, re, length, n=200):

#     x = np.linspace(0, length, n)

#     y = rt + (re - rt) * (x/length)**2

#     return list(zip(x, y))

import numpy as np


def generate_contour(rt, re, length, theta_e=12, n=200):

    x = np.linspace(0, length, n)

    y0 = rt
    ye = re

    me = np.tan(np.radians(theta_e))

    A = np.array([
        [0, 0, 1],
        [length**2, length, 1],
        [2*length, 1, 0]
    ])

    B = np.array([
        y0,
        ye,
        me
    ])

    a, b, c = np.linalg.solve(A, B)

    y = a*x**2 + b*x + c

    return list(zip(x, y))


      