"""Assembly of the full 2D engine contour in throat-centered coordinates."""

from __future__ import annotations

from typing import List, Tuple

from geometry.converging import converging_parabola
from geometry.throat import throat_region
from geometry.rao import rao_bell_contour

PointList = List[Tuple[float, float]]

_BELL_LENGTH_PERCENT = 80


def _dedupe_join(points: PointList) -> PointList:
    """Remove only consecutive duplicate points."""
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
    """
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
    """
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

    conv_pts = converging_parabola(
        rc=rc,
        x_start=x_ch_end,
        x_end=entrant_start_x,
        y_end=entrant_start_y,
        n=100,
    )

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

    return {
        "chamber": chamber_pts,
        "converging": conv_pts,
        "throat": throat_data["contour"],
        "bell": bell_pts,
        "contour": contour,
        "theta_n_deg": bell_data["theta_n_deg"],
        "theta_e_deg": bell_data["theta_e_deg"],
        "bell_length": bell_data["bell_length"],
    }