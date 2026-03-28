import numpy as np


class RaoBell:
    """
    Calculates the nozzle bell contour using a cubic polynomial approximation.
    """

    def __init__(self, theta_n=30, theta_e=12):
        """
        Args:
            theta_n (float): Initial nozzle angle in degrees.
            theta_e (float): Exit nozzle angle in degrees.
        """
        self.theta_n = np.radians(theta_n)
        self.theta_e = np.radians(theta_e)

    def length(self, rt, re):
        """
        Calculates the 80% length of a 15-degree equivalent cone.

        Args:
            rt (float): Throat radius.
            re (float): Exit radius.

        Returns:
            float: The characteristic length L.
        """
        cone_angle = np.radians(15)
        # Standard calculation for an 80% bell
        l_cone = (re - rt) / np.tan(cone_angle)
        
        return 0.8 * l_cone

    def contour(self, rt, re, L, x0=0.0, n=200):
        """
        Generates the bell profile coordinates using a cubic spline.

        Args:
            rt (float): Throat radius.
            re (float): Exit radius.
            L (float): Axial length of the bell.
            x0 (float): Starting axial position.
            n (int): Number of points.

        Returns:
            list: A list of (x, y) coordinates for the bell section.
        """
        x1 = x0
        x2 = x0 + L

        y1 = rt
        y2 = re

        m1 = np.tan(self.theta_n)
        m2 = np.tan(self.theta_e)

        # Matrix A defines the cubic system: y = ax^3 + bx^2 + cx + d
        # Rows represent: y(x1), y(x2), y'(x1), y'(x2)
        matrix_a = np.array([
            [x1**3, x1**2, x1, 1],
            [x2**3, x2**2, x2, 1],
            [3 * x1**2, 2 * x1, 1, 0],
            [3 * x2**2, 2 * x2, 1, 0]
        ])

        vector_b = np.array([y1, y2, m1, m2])

        # Solve for coefficients [a, b, c, d]
        a, b, c, d = np.linalg.solve(matrix_a, vector_b)

        x = np.linspace(x1, x2, n)
        y = a * x**3 + b * x**2 + c * x + d

        return list(zip(x, y))