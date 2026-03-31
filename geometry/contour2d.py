<<<<<<< HEAD
=======
"""Assembly of the full 2D engine contour in throat-centered coordinates.

from __future__ import annotations

from typing import List, Tuple

>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
from geometry.converging import converging_parabola
from geometry.throat import throat_region
from geometry.rao import rao_bell_contour

<<<<<<< HEAD

def build_full_contour(rt, re, rc, chamber_length, conv_length):
    """
    Stitches chamber, converging, and Rao bell sections into a single contour.

    Args:
        rt, re, rc (float): Radii for throat, exit, and chamber.
        chamber_length (float): Length of the cylindrical chamber.
        conv_length (float): Axial length of the converging section.

    Returns:
        dict: A dictionary containing points for each section and the full contour.
    """
    # 1. Define the cylindrical chamber section
    # Points are (x, y) coordinates
    chamber_pts = [
        (-chamber_length, rc),
        (0.0, rc)
    ]

    # 2. Generate converging section points
=======
PointList = List[Tuple[float, float]]

_BELL_LENGTH_PERCENT = 80


def _dedupe_join(points: PointList) -> PointList:
    Remove only consecutive duplicate points.
    if not points:
        return []

    clean = [points[0]]
    for pt in points[1:]:
        if pt != clean[-1]:
            clean.append(pt)
    return clean


def build_full_contour(
    rt: float,
    re: float,
    rc: float,
    chamber_length: float,
    conv_length: float,
    bell_length_percent: int = _BELL_LENGTH_PERCENT,
) -> dict:
    
    Build the full internal engine wall contour using throat-centered coordinates.

    Geometry order
    --------------
    1. Chamber cylindrical section
    2. Converging section
    3. Throat entrant arc
    4. Throat exit arc
    5. Rao/TOP bell section

    Parameters
    ----------
    rt : float
        Throat radius [m]
    re : float
        Exit radius [m]
    rc : float
        Chamber radius [m]
    chamber_length : float
        Cylindrical chamber length [m]
    conv_length : float
        Converging section length [m]
    bell_length_percent : int
        Rao bell length percentage: 60, 80, or 90

    Returns
    -------
    dict
        chamber     : chamber points
        converging  : converging points
        throat      : throat-region contour
        bell        : bell contour
        contour     : full stitched contour
        theta_n_deg : bell inlet angle
        theta_e_deg : bell exit angle
        bell_length : bell axial length
    
    # --- Throat + bell first, because converging must connect into entrant arc ---
    bell_data = rao_bell_contour(rt=rt, re=re, length_percent=bell_length_percent)
    theta_n_deg = bell_data["theta_n_deg"]

    throat_data = throat_region(rt=rt, theta_n_deg=theta_n_deg)
    entrant = throat_data["entrant"]
    exit_arc = throat_data["exit"]

    # --- Chamber ---
    x_ch_start = -(chamber_length + conv_length)
    x_ch_end = -conv_length
    chamber_pts: PointList = [
        (x_ch_start, rc),
        (x_ch_end, rc),
    ]

    # --- Converging section ---
    entrant_start_x, entrant_start_y = entrant[0]

>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
    conv_pts = converging_parabola(
        rc=rc,
        x_start=x_ch_end,
        x_end=entrant_start_x,
        y_end=entrant_start_y,
        n=100,
    )

<<<<<<< HEAD
    # 3. Generate the Rao Bell (nozzle) section
    rao = RaoBell()
    nozzle_length = rao.length(rt, re)

    # Use the end of the converging section as the start for the bell
    bell_pts = rao.contour(
        rt=rt,
        re=re,
        L=nozzle_length,
        x0=conv_pts[-1][0]
    )

    # 4. Stitch sections together while avoiding duplicate junction points
    full_contour = list(chamber_pts)

    for section in [conv_pts, bell_pts]:
        if section:
            # If the last point of the contour matches the first of the new section,
            # skip the first point of the new section to avoid duplicates.
            start_idx = 1 if full_contour[-1] == section[0] else 0
            full_contour.extend(section[start_idx:])
=======
    # --- Bell ---
    bell_pts = bell_data["contour"]

    # --- Stitch all sections carefully ---
    contour: PointList = []
    contour.extend(chamber_pts)
    contour.extend(conv_pts[1:])
    contour.extend(entrant[1:])
    contour.extend(exit_arc[1:])
    contour.extend(bell_pts[1:])

    contour = _dedupe_join(contour)
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987

    return {
        "chamber": chamber_pts,
        "converging": conv_pts,
        "throat": throat_data["contour"],
        "bell": bell_pts,
<<<<<<< HEAD
        "full_contour": full_contour,
        "nozzle_length": nozzle_length
=======
        "contour": contour,
        "theta_n_deg": bell_data["theta_n_deg"],
        "theta_e_deg": bell_data["theta_e_deg"],
        "bell_length": bell_data["bell_length"],
    }"""

"""Assembly of the full 2D engine contour in throat-centered coordinates."""

import math

from geometry.converging import converging_section
from geometry.throat import throat_region
from geometry.rao import rao_bell_contour

PointList = list[tuple[float, float]]

_BELL_LENGTH_PERCENT = 80
_ENTRANT_RADIUS_FACTOR = 1.5
_ENTRANT_START_ANGLE_DEG = -135.0


def _dedupe_join(points: PointList) -> PointList:
    """Remove consecutive near-duplicate points."""
    if not points:
        return []

    clean = [points[0]]
    for pt in points[1:]:
        if not (math.isclose(pt[0], clean[-1][0]) and math.isclose(pt[1], clean[-1][1])):
            clean.append(pt)
    return clean


def _entrant_arc_start_slope(theta_start_deg: float) -> float:
    """
    Compute the wall slope dy/dx at the start of the entrant arc.

    The entrant arc is parametric: x = Ru*cos(theta), y = cy + Ru*sin(theta)
    so dy/dx = cos(theta) / (-sin(theta)) = -cot(theta).
    """
    theta = math.radians(theta_start_deg)
    return -math.cos(theta) / math.sin(theta)


def build_full_contour(
    rt: float,
    re: float,
    rc: float,
    chamber_length: float,
    conv_length: float,
    bell_length_percent: int = _BELL_LENGTH_PERCENT,
) -> dict:
    """
    Build the full internal engine wall contour in throat-centered coordinates.

    Geometry order
    --------------
    1. Chamber cylindrical section
    2. Converging section (cubic, C1 at both ends)
    3. Throat entrant arc  (radius 1.5*rt)
    4. Throat exit arc     (radius 0.382*rt)
    5. Rao/TOP bell        (quadratic Bezier)

    Parameters
    ----------
    rt                 : throat radius [m]
    re                 : exit radius [m]
    rc                 : chamber radius [m]
    chamber_length     : cylindrical chamber length [m]
    conv_length        : converging section axial length [m]
    bell_length_percent: Rao bell length percentage (60, 80, or 90)

    Returns
    -------
    dict with keys: chamber, converging, throat, bell, contour,
                    theta_n_deg, theta_e_deg, bell_length
    """
    # --- 1. Bell and throat arcs (computed first to get theta_n and entrant start) ---
    bell_data = rao_bell_contour(rt=rt, re=re, length_percent=bell_length_percent)
    theta_n_deg = bell_data["theta_n_deg"]

    throat_data = throat_region(rt=rt, theta_n_deg=theta_n_deg)
    entrant = throat_data["entrant"]
    exit_arc = throat_data["exit"]

    # --- 2. Chamber ---
    x_ch_start = -(chamber_length + conv_length)
    x_ch_end = -conv_length
    chamber_pts: PointList = [
        (x_ch_start, rc),
        (x_ch_end,   rc),
    ]

    # --- 3. Converging section (cubic, C1 into entrant arc) ---
    entrant_start_x, entrant_start_y = entrant[0]
    slope_end = _entrant_arc_start_slope(_ENTRANT_START_ANGLE_DEG)

    conv_pts = converging_section(
        rc=rc,
        x_start=x_ch_end,
        x_end=entrant_start_x,
        y_end=entrant_start_y,
        slope_end=slope_end,
        n=100,
    )

    # --- 4. Bell ---
    bell_pts = bell_data["contour"]

    # --- 5. Stitch ---
    contour: PointList = []
    contour.extend(chamber_pts)
    contour.extend(conv_pts[1:])
    contour.extend(entrant[1:])
    contour.extend(exit_arc[1:])
    contour.extend(bell_pts[1:])
    contour = _dedupe_join(contour)

    return {
        "chamber":    chamber_pts,
        "converging": conv_pts,
        "throat":     throat_data["contour"],
        "bell":       bell_pts,
        "contour":    contour,
        "theta_n_deg": bell_data["theta_n_deg"],
        "theta_e_deg": bell_data["theta_e_deg"],
        "bell_length": bell_data["bell_length"],
>>>>>>> 3bcdbe14c7fb33c30b012ea16b1b5126c1981987
    }