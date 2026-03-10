import numpy as np


class RaoBell:

    def __init__(self,
                 theta_n_deg=30,
                 theta_e_deg=15):

        self.theta_n = np.radians(theta_n_deg)
        self.theta_e = np.radians(theta_e_deg)


    def nozzle_length(self, rt, re):

        L = (re - rt) / np.tan(self.theta_n)

        return 0.8 * L


    def bell_curve(self, rt, re, L, x_start=0, n=200):

        x = np.linspace(x_start, x_start + L, n)

        s = (x - x_start) / L

        y = rt + (re - rt) * (s**2)

        return list(zip(x, y))