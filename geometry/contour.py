To align your code with PEP 8 standards while respecting your preference for capitalized propulsion constants, here is the refactored version.

In this context, I have treated RT, RE, and L (Length) as the standard propulsion constants to be kept in uppercase.

Python
import numpy as np


def generate_contour(RT, RE, L, theta_e=12, n=200):
    """
    Generates a parabolic nozzle contour based on boundary conditions.

    Args:
        RT (float): Throat radius.
        RE (float): Exit radius.
        L (float): Nozzle length.
        theta_e (float): Exit angle in degrees.
        n (int): Number of points to generate.

    Returns:
        list: A list of (x, y) coordinates for the nozzle profile.
    """
    x = np.linspace(0, L, n)

    # Boundary conditions for the parabola: y = ax^2 + bx + c
    y0 = RT
    ye = RE
    me = np.tan(np.radians(theta_e))

    # Matrix A represents the system of equations at x=0 and x=L
    # 1. c = y0 (at x=0)
    # 2. a*L^2 + b*L + c = ye (at x=L)
    # 3. 2*a*L + b = me (derivative at x=L)
    matrix_a = np.array([
        [0, 0, 1],
        [L**2, L, 1],
        [2 * L, 1, 0]
    ])

    vector_b = np.array([y0, ye, me])

    # Solve for coefficients [a, b, c]
    a, b, c = np.linalg.solve(matrix_a, vector_b)

    # Calculate the radial profile
    y = a * x**2 + b * x + c

    return list(zip(x, y))