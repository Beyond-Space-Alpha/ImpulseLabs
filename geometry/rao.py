import numpy as np


class RaoBell:

    def __init__(self, theta_n=30, theta_e=12):

        self.theta_n = np.radians(theta_n)
        self.theta_e = np.radians(theta_e)

    def length(self, rt, re):

        cone_angle = np.radians(15)

        L_cone = (re - rt) / np.tan(cone_angle)

        return 0.8 * L_cone

    
    def contour(self, rt, re, L, x0=0.0, n=200):

     x1 = x0
     x2 = x0 + L

     y1 = rt
     y2 = re

     m1 = np.tan(self.theta_n)
     m2 = np.tan(self.theta_e)

     A = np.array([
        [x1**3, x1**2, x1, 1],
        [x2**3, x2**2, x2, 1],
        [3*x1**2, 2*x1, 1, 0],
        [3*x2**2, 2*x2, 1, 0]
     ])

     B = np.array([y1, y2, m1, m2])

     a, b, c, d = np.linalg.solve(A, B)

     x = np.linspace(x1, x2, n)
     y = a*x**3 + b*x**2 + c*x + d

     return list(zip(x, y))