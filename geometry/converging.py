# import numpy as np

# def converging_section(rc, rt, x_start, length=0.05, n=50):

#     x = np.linspace(x_start, x_start + length, n)

#     y = rc + (rt - rc) * ((x - x_start) / length)

#     return list(zip(x, y))

import numpy as np


def converging_section(rc, rt, x_start, length=0.05, n=100):

    x0 = x_start
    x1 = x_start + length

    y0 = rc
    y1 = rt

    A = np.array([
        [x0**2, x0, 1],
        [x1**2, x1, 1],
        [2*x1, 1, 0]
    ])

    B = np.array([
        y0,
        y1,
        0
    ])

    a, b, c = np.linalg.solve(A, B)

    x = np.linspace(x0, x1, n)

    y = a*x**2 + b*x + c

    return list(zip(x, y)), length