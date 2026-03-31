"""Rao bell nozzle geometry using a quadratic Bezier representation."""


<<<<<<< HEAD
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
=======
import math

PointList = list[tuple[float, float]]

# Rao/TOP wall-angle tables commonly used for 60%, 80%, 90% bell lengths.
# Rows correspond approximately to area ratio values:
# 4, 5, 10, 20, 30, 40, 50, 100
_AREA_RATIOS = [4, 5, 10, 20, 30, 40, 50, 100]

_THETA_N_TABLE = {
    60: [26.5, 28.0, 32.0, 35.0, 36.2, 37.1, 35.0, 40.0],
    80: [21.5, 23.0, 26.3, 28.8, 30.0, 31.0, 31.5, 33.5],
    90: [20.0, 21.0, 24.0, 27.0, 28.5, 29.5, 30.2, 32.0],
}

_THETA_E_TABLE = {
    60: [20.5, 20.0, 16.0, 12.5, 11.0, 10.5, 10.0, 8.0],
    80: [14.0, 13.5, 11.0, 9.0, 8.5, 8.0, 7.5, 7.0],
    90: [11.5, 11.0, 9.0, 8.0, 7.5, 7.0, 6.5, 6.0],
}


def _interp(x: float, xp: list[float], fp: list[float]) -> float:
    """Simple piecewise-linear interpolation with end clamping."""
    if x <= xp[0]:
        return float(fp[0])
    if x >= xp[-1]:
        return float(fp[-1])

    for i in range(len(xp) - 1):
        x0, x1 = xp[i], xp[i + 1]
        if x0 <= x <= x1:
            y0, y1 = fp[i], fp[i + 1]
            t = (x - x0) / (x1 - x0)
            return float(y0 + t * (y1 - y0))

    return float(fp[-1])


def find_wall_angles(area_ratio: float, length_percent: int = 80) -> tuple[float, float]:
    """
    Interpolate Rao/TOP inlet and exit wall angles.

    Parameters
    ----------
    area_ratio : float
        Expansion ratio Ae/At [-]
    length_percent : int
        Bell length percentage, typically 60, 80, or 90

    Returns
    -------
    tuple[float, float]
        theta_n_deg, theta_e_deg
    """
    if length_percent not in _THETA_N_TABLE:
        raise ValueError(
            f"Unsupported bell length percentage: {length_percent}. "
            "Use one of 60, 80, or 90."
        )

    theta_n = _interp(area_ratio, _AREA_RATIOS, _THETA_N_TABLE[length_percent])
    theta_e = _interp(area_ratio, _AREA_RATIOS, _THETA_E_TABLE[length_percent])

    return theta_n, theta_e


def bell_length(rt: float, re: float, length_percent: int = 80) -> float:
    """
    Compute bell length from equivalent 15-degree conical nozzle length.

    Parameters
    ----------
    rt : float
        Throat radius [m]
    re : float
        Exit radius [m]
    length_percent : int
        Bell length percentage relative to the conical reference

    Returns
    -------
    float
        Bell length [m]
    """
    if length_percent <= 0:
        raise ValueError("length_percent must be positive.")

    theta_cone = math.radians(15.0)
    l_cone = (re - rt) / math.tan(theta_cone)
    return (length_percent / 100.0) * l_cone


def bell_start_point(rt: float, theta_n_deg: float) -> tuple[float, float]:
    """
    End point of the downstream throat arc (radius 0.382*rt), where the bell begins.

    Parameters
    ----------
    rt : float
        Throat radius [m]
    theta_n_deg : float
        Bell inlet angle [deg]

    Returns
    -------
    tuple[float, float]
        Start point N = (x_n, y_n)
    """
    rd = 0.382 * rt
    theta = math.radians(theta_n_deg - 90.0)

    cx = 0.0
    cy = rt + rd

    x_n = cx + rd * math.cos(theta)
    y_n = cy + rd * math.sin(theta)

    return x_n, y_n


def control_point(
    start_point: tuple[float, float],
    exit_point: tuple[float, float],
    theta_n_deg: float,
    theta_e_deg: float,
) -> tuple[float, float]:
    """
    Compute the quadratic Bezier control point from the intersection
    of tangent lines at start and exit.

    Parameters
    ----------
    start_point : tuple[float, float]
        Bell start point N
    exit_point : tuple[float, float]
        Bell exit point E
    theta_n_deg : float
        Inlet wall angle [deg]
    theta_e_deg : float
        Exit wall angle [deg]

    Returns
    -------
    tuple[float, float]
        Control point Q
    """
    x_n, y_n = start_point
    x_e, y_e = exit_point

    m_n = math.tan(math.radians(theta_n_deg))
    m_e = math.tan(math.radians(theta_e_deg))

    # Intersection of:
    # y = y_n + m_n (x - x_n)
    # y = y_e + m_e (x - x_e)
    x_q = (y_e - y_n + m_n * x_n - m_e * x_e) / (m_n - m_e)
    y_q = y_n + m_n * (x_q - x_n)

    return x_q, y_q


def quadratic_bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    n: int = 200,
) -> PointList:
    """
    Generate a quadratic Bezier curve.

    Parameters
    ----------
    p0 : tuple[float, float]
        Start point
    p1 : tuple[float, float]
        Control point
    p2 : tuple[float, float]
        End point
    n : int
        Number of points

    Returns
    -------
    list[tuple[float, float]]
        Bezier curve points
    """
    pts: PointList = []

    for i in range(n):
        t = i / (n - 1)
        omt = 1.0 - t

        x = omt * omt * p0[0] + 2.0 * omt * t * p1[0] + t * t * p2[0]
        y = omt * omt * p0[1] + 2.0 * omt * t * p1[1] + t * t * p2[1]

        pts.append((x, y))

    return pts


def rao_bell_contour(rt: float, re: float, length_percent: int = 80, n: int = 200) -> dict:
    """
    Build a throat-centered Rao/TOP bell contour using a quadratic Bezier curve.

    Parameters
    ----------
    rt : float
        Throat radius [m]
    re : float
        Exit radius [m]
    length_percent : int
        Bell length percentage: 60, 80, or 90
    n : int
        Number of points

    Returns
    -------
    dict
        area_ratio   : float
        theta_n_deg  : float
        theta_e_deg  : float
        bell_length  : float
        start_point  : tuple
        control_point: tuple
        exit_point   : tuple
        contour      : list[(x, y)]
    """
    area_ratio = (re / rt) ** 2
    theta_n_deg, theta_e_deg = find_wall_angles(area_ratio, length_percent=length_percent)

    l_bell = bell_length(rt, re, length_percent=length_percent)

    start_point = bell_start_point(rt, theta_n_deg)
    exit_point = (l_bell, re)
    q_point = control_point(start_point, exit_point, theta_n_deg, theta_e_deg)

    contour = quadratic_bezier(start_point, q_point, exit_point, n=n)

    return {
        "area_ratio": area_ratio,
        "theta_n_deg": theta_n_deg,
        "theta_e_deg": theta_e_deg,
        "bell_length": l_bell,
        "start_point": start_point,
        "control_point": q_point,
        "exit_point": exit_point,
        "contour": contour,
    }
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
