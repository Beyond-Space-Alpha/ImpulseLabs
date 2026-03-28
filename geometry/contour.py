import numpy as np


def generate_contour(rt, re, length, theta_e=12, n=200):
    """
    Generates a parabolic nozzle contour based on boundary conditions.
    
    Args:
        rt (float): Throat radius.
        re (float): Exit radius.
        length (float): Nozzle length.
        theta_e (float): Exit angle in degrees.
        n (int): Number of points to generate.
    """
    x = np.linspace(0, length, n)

    # Boundary conditions for the parabola: y = ax^2 + bx + c
    y0 = rt
    ye = re
    me = np.tan(np.radians(theta_e))

    # Matrix A represents the system of equations at x=0 and x=length
    # 1. c = y0 (at x=0)
    # 2. a*L^2 + b*L + c = ye (at x=L)
    # 3. 2*a*L + b = me (derivative at x=L)
    A = np.array([
        [0, 0, 1],
        [length**2, length, 1],
        [2 * length, 1, 0]
    ])

    B = np.array([y0, ye, me])

    # Solve for coefficients [a, b, c]
    a, b, c = np.linalg.solve(A, B)

    # Calculate the radial profile
    y = a * x**2 + b * x + c

    return list(zip(x, y))