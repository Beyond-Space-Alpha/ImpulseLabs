# import numpy as np

# def converging_section(rc, rt, x_start, length=0.05, n=50):

#     x = np.linspace(x_start, x_start + length, n)

#     y = rc + (rt - rc) * ((x - x_start) / length)

#     return list(zip(x, y))

import numpy as np


def converging_section(rc, rt, x_start, angle_deg=45, n=50):

    angle = np.radians(angle_deg)

    length = (rc - rt) / np.tan(angle)

    x = np.linspace(x_start, x_start + length, n)

    y = rc - (x - x_start) * np.tan(angle)

    return list(zip(x, y)), length