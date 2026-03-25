"""Converging section geometry upstream of the throat entrant arc."""

from __future__ import annotations

import numpy as np
from typing import List, Tuple

PointList = List[Tuple[float, float]]


def converging_parabola(
    rc: float,
    x_start: float,
    x_end: float,
    y_end: float,
    n: int = 100,
) -> PointList:
    """
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
    """
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