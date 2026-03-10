import numpy as np

def converging_section(rc, rt, x_start, length=0.05, n=50):

    x = np.linspace(x_start, x_start + length, n)

    y = rc + (rt - rc) * ((x - x_start) / length)

    return list(zip(x, y))