"""

Converging section geometry upstream of the throat entrant arc.

from __future__ import annotations

import numpy as np

PointList = list[Tuple[float, float]]

<<<<<<< HEAD
def converging_parabola(rc, rt, x0, length, n=80):
    """
    Generates a parabolic converging section from chamber to throat.

    Args:
        rc (float): Chamber radius.
        rt (float): Throat radius.
        x0 (float): Starting axial position.
        length (float): Axial length of the converging section.
        n (int): Number of points to generate.

    Returns:
        list: A list of (x, y) coordinates for the converging profile.
    """
    x = np.linspace(x0, x0 + length, n)

    # s is the normalized axial distance (0 to 1)
    s = (x - x0) / length

    # Parabolic profile: y decreases from rc to rt
    # This provides a smooth transition with zero slope at the chamber interface
    y = rc - (rc - rt) * (s**2)

    return list(zip(x, y))
  
=======

def converging_parabola(
    rc: float,
    x_start: float,
    x_end: float,
    y_end: float,
    n: int = 100,
) -> PointList:
    
    Generate a simple converging parabolic wall from chamber radius to the
    start of the throat entrant arc.

    The curve is built in throat-centered coordinates:
    - chamber is upstream (negative x)
    - throat is at x = 0

    Boundary conditions:
    - y(x_start) = rc
    - y(x_end)   = y_end
    - dy/dx at x_start = 0   (flat chamber-to-converging junction)

    Parameters
    ----------
    rc : float
        Chamber radius [m]
    x_start : float
        Start x-coordinate of converging section [m]
    x_end : float
        End x-coordinate of converging section [m]
    y_end : float
        End radius at the start of the entrant arc [m]
    n : int
        Number of points

    Returns
    -------
    list[tuple[float, float]]
        Ordered (x, y) points from chamber toward throat
    
    if x_end <= x_start:
        raise ValueError(
            f"x_end must be greater than x_start. Got x_start={x_start}, x_end={x_end}."
        )

    x = np.linspace(x_start, x_end, n)

    # Shift coordinate so polynomial is in local variable s = x - x_start
    s = x - x_start
    L = x_end - x_start

    # Quadratic: y = a*s^2 + b*s + c
    # Conditions:
    # y(0) = rc
    # y(L) = y_end
    # y'(0) = 0
    c = rc
    b = 0.0
    a = (y_end - rc) / (L ** 2)

    y = a * s**2 + b * s + c

    return list(zip(x.tolist(), y.tolist()))

"""


"""Converging section geometry upstream of the throat entrant arc."""


import numpy as np

PointList = list[tuple[float, float]]


def converging_section(
    rc: float,
    x_start: float,
    x_end: float,
    y_end: float,
    slope_end: float,
    n: int = 100,
) -> PointList:
    """
    Generate the converging wall from chamber radius to the start of the
    throat entrant arc using a cubic polynomial.

    Boundary conditions:
        y(x_start)  = rc          flat chamber junction
        y'(x_start) = 0           zero slope at chamber
        y(x_end)    = y_end       matches entrant arc start radius
        y'(x_end)   = slope_end   matches entrant arc start slope

    Parameters
    ----------
    rc         : chamber radius [m]
    x_start    : start x-coordinate (chamber end) [m]
    x_end      : end x-coordinate (entrant arc start) [m]
    y_end      : radius at entrant arc start [m]
    slope_end  : wall slope dy/dx at entrant arc start [-]
    n          : number of points

    Returns
    -------
    list[tuple[float, float]]
    """
    if x_end <= x_start:
        raise ValueError(
            f"x_end must be greater than x_start. "
            f"Got x_start={x_start:.6f}, x_end={x_end:.6f}."
        )

    L = x_end - x_start

    # Cubic in local coordinate s = x - x_start
    # y = a*s^3 + b*s^2 + c*s + d
    # y(0)  = rc     → d = rc
    # y'(0) = 0      → c = 0
    # y(L)  = y_end  → a*L^3 + b*L^2 = y_end - rc
    # y'(L) = slope  → 3*a*L^2 + 2*b*L = slope_end

    d = rc
    c = 0.0

    # Solve 2x2 system:
    # [ L^3   L^2 ] [a]   [y_end - rc  ]
    # [ 3L^2  2L  ] [b] = [slope_end   ]
    A = np.array([
        [L**3,    L**2],
        [3.0*L**2, 2.0*L],
    ])
    B = np.array([y_end - rc, slope_end])

    a, b = np.linalg.solve(A, B)

    s = np.linspace(0.0, L, n)
    y = a * s**3 + b * s**2 + c * s + d
    x = s + x_start

    return list(zip(x.tolist(), y.tolist()))
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
