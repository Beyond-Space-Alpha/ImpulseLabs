from geometry.converging import converging_parabola
from geometry.rao import RaoBell


def build_full_contour(rt, re, rc, chamber_length, conv_length):
    """
    Stitches chamber, converging, and Rao bell sections into a single contour.
    
    Args:
        rt, re, rc (float): Radii for throat, exit, and chamber.
        chamber_length (float): Length of the cylindrical chamber.
        conv_length (float): Axial length of the converging section.
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

    bell_pts = rao.contour(
        rt=rt,
        re=re,
        L=nozzle_length,
        x0=conv_pts[-1][0]
    )

    # 4. Stitch sections together while avoiding duplicate junction points
    contour = list(chamber_pts)

    # Stitching converging section
    if contour and conv_pts and contour[-1] == conv_pts[0]:
        contour.extend(conv_pts[1:])
    else:
        contour.extend(conv_pts)

    # Stitching bell section
    if contour and bell_pts and contour[-1] == bell_pts[0]:
        contour.extend(bell_pts[1:])
    else:
        contour.extend(bell_pts)

    return {
        "chamber": chamber_pts,
        "converging": conv_pts,
        "bell": bell_pts,
        "contour": contour,
        "nozzle_length": nozzle_length
    }