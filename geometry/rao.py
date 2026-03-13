import numpy as np


class RaoBell:

    def __init__(self, theta_n=30, theta_e=12):

        self.theta_n = np.radians(theta_n)
        self.theta_e = np.radians(theta_e)

    def length(self, rt, re):

        cone_angle = np.radians(15)

        L_cone = (re - rt) / np.tan(cone_angle)

        return 0.8 * L_cone


    def contour(self, rt, re, L, x0=0, n=200):

        x = np.linspace(x0, x0 + L, n)

        y0 = rt
        ye = re

        me = np.tan(self.theta_e)

        A = np.array([
            [x0**2, x0, 1],
            [(x0 + L)**2, (x0 + L), 1],
            [2 * (x0 + L), 1, 0]
        ])

        B = np.array([
            y0,
            ye,
            me
        ])

        a, b, c = np.linalg.solve(A, B)

        y = a * x**2 + b * x + c

        return list(zip(x, y))