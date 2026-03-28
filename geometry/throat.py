"""Throat-region geometry for a Rao bell nozzle."""

import math

PointList = list[tuple[float, float]]

_ENTRANT_RADIUS_FACTOR = 1.5
_EXIT_RADIUS_FACTOR = 0.382


<<<<<<< HEAD
def throat_fillet(rt, radius=0.02, x0=0, n=40):
    """
    Generates a circular arc fillet for the nozzle throat transition.

    Args:
        rt (float): Throat radius.
        radius (float): Radius of the fillet arc.
        x0 (float): Axial center of the fillet arc.
        n (int): Number of points to generate.

    Returns:
        list: A list of (x, y) coordinates for the circular fillet.
    """
    # Angle spans from -90 degrees (vertical) to 0 degrees (horizontal)
    # to create the transition from the converging section to the throat
    theta = np.linspace(-np.pi / 2, 0, n)
=======
def throat_entrant_arc(rt: float, n: int = 60) -> PointList:
    """
    Generate the upstream throat entrant circular arc.

    The standard Rao/TOP entrant throat blend uses radius:
        R_u = 1.5 * rt
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987

    The arc is parameterized from -135 deg to -90 deg so that:
    - it approaches the throat from upstream
    - it ends exactly at the throat point (x=0, y=rt)

<<<<<<< HEAD
    return list(zip(x, y))
=======
    Parameters
    ----------
    rt : float
        Throat radius [m]
    n : int
        Number of points on the arc

    Returns
    -------
    list[tuple[float, float]]
        Ordered (x, y) points from upstream toward the throat
    """
    ru = _ENTRANT_RADIUS_FACTOR * rt

    cx = 0.0
    cy = rt + ru

    theta_start = math.radians(-135.0)
    theta_end = math.radians(-90.0)

    pts: PointList = []
    for i in range(n):
        t = i / (n - 1)
        theta = theta_start + t * (theta_end - theta_start)
        x = cx + ru * math.cos(theta)
        y = cy + ru * math.sin(theta)
        pts.append((x, y))

    return pts


def throat_exit_arc(rt: float, theta_n_deg: float, n: int = 60) -> PointList:
    """
    Generate the downstream throat exit circular arc.

    Standard Rao/TOP downstream throat blend uses radius:
        R_d = 0.382 * rt

    The arc starts at the throat point (x=0, y=rt), where the wall tangent is horizontal,
    and ends where the wall tangent reaches theta_n.

    Parameters
    ----------
    rt : float
        Throat radius [m]
    theta_n_deg : float
        Bell inlet angle [deg]
    n : int
        Number of points on the arc

    Returns
    -------
    list[tuple[float, float]]
        Ordered (x, y) points from throat toward bell start
    """
    rd = _EXIT_RADIUS_FACTOR * rt

    cx = 0.0
    cy = rt + rd

    theta_start = math.radians(-90.0)
    theta_end = math.radians(theta_n_deg - 90.0)

    pts: PointList = []
    for i in range(n):
        t = i / (n - 1)
        theta = theta_start + t * (theta_end - theta_start)
        x = cx + rd * math.cos(theta)
        y = cy + rd * math.sin(theta)
        pts.append((x, y))

    return pts


def throat_region(rt: float, theta_n_deg: float, n_entrant: int = 60, n_exit: int = 60) -> dict:
    """
    Build the full throat region:
        entrant arc -> throat point -> exit arc

    Parameters
    ----------
    rt : float
        Throat radius [m]
    theta_n_deg : float
        Bell inlet angle [deg]
    n_entrant : int
        Number of points for entrant arc
    n_exit : int
        Number of points for exit arc

    Returns
    -------
    dict
        entrant : list[(x, y)]
        exit    : list[(x, y)]
        throat  : tuple[float, float]
        contour : combined throat-region contour
    """
    entrant = throat_entrant_arc(rt, n=n_entrant)
    exit_arc = throat_exit_arc(rt, theta_n_deg=theta_n_deg, n=n_exit)

    throat_point = (0.0, rt)

    contour = entrant + exit_arc[1:]

    return {
        "entrant": entrant,
        "exit": exit_arc,
        "throat": throat_point,
        "contour": contour,
    }
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
