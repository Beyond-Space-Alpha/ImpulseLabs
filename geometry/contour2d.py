from geometry.converging import converging_parabola
from geometry.rao import RaoBell


def build_full_contour(RT, RE, RC, L_CHAMBER, L_CONV):
    """
    Stitches chamber, converging, and Rao bell sections into a single contour.

    Args:
        RT (float): Throat radius.
        RE (float): Exit radius.
        RC (float): Chamber radius.
        L_CHAMBER (float): Length of the cylindrical chamber.
        L_CONV (float): Axial length of the converging section.

    Returns:
        dict: A dictionary containing points for each section and the full contour.
    """
    # 1. Define the cylindrical chamber section
    # Points are (x, y) coordinates
    chamber_pts = [
        (-L_CHAMBER, RC),
        (0.0, RC)
    ]

    # 2. Generate converging section points
    conv_pts = converging_parabola(
        rc=RC,
        rt=RT,
        x0=0.0,
        length=L_CONV
    )

    # 3. Generate the Rao Bell (nozzle) section
    rao = RaoBell()
    L_NOZZLE = rao.length(RT, RE)

    # Note: Using conv_pts[-1][0] as the x_start for the bell
    bell_pts = rao.contour(
        rt=RT,
        re=RE,
        L=L_NOZZLE,
        x0=conv_pts[-1][0]
    )

    # 4. Stitch sections together
    # We use list slicing [1:] to avoid duplicating junction points
    contour = list(chamber_pts)
    
    if conv_pts:
        # Check if the last chamber point is identical to first converging point
        start_idx = 1 if contour[-1] == conv_pts[0] else 0
        contour.extend(conv_pts[start_idx:])

    if bell_pts:
        # Check if the last converging point is identical to first bell point
        start_idx = 1 if contour[-1] == bell_pts[0] else 0
        contour.extend(bell_pts[start_idx:])

    return {
        "chamber": chamber_pts,
        "converging": conv_pts,
        "bell": bell_pts,
        "full_contour": contour,
        "L_NOZZLE": L_NOZZLE
    }