import numpy as np


class RaoBell:

    def __init__(self, theta_n=30, theta_e=15):

        self.theta_n = np.radians(theta_n)
        self.theta_e = np.radians(theta_e)

    def length(self, rt, re):

        conical = (re - rt) / np.tan(self.theta_n)

        return 0.8 * conical

    def contour(self, rt, re, L, x0=0, n=200):

        x = np.linspace(x0, x0 + L, n)

        s = (x - x0) / L

        y = rt + (re - rt) * (s ** 2)

        return list(zip(x, y))