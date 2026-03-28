from geometry.converging import converging_parabola
from geometry.rao import RaoBell


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
    conv_pts = converging_parabola(
        rc=rc,
        rt=rt,
        x0=0.0,
        length=conv_length
    )

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

    return {
        "chamber": chamber_pts,
        "converging": conv_pts,
        "bell": bell_pts,
        "full_contour": full_contour,
        "nozzle_length": nozzle_length
    }