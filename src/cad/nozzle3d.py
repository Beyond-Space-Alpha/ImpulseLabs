import cadquery as cq


def clean_points(points):
    """Remove consecutive duplicate points."""
    clean = []
    for p in points:
        if not clean or p != clean[-1]:
            clean.append(p)
    return clean


def create_3d_nozzle(contour):
    """
    Revolve a 2D (x, r) contour about the x-axis into a 3D solid.

    Parameters
    ----------
    contour : list[tuple[float, float]]
        Full upper-wall contour in (x, radius) coordinates.

    Returns
    -------
    cq.Workplane
        3D solid nozzle/chamber body.
    """
    contour = clean_points(contour)

    if len(contour) < 2:
        raise ValueError("Contour must contain at least two points.")

    pts = [(x, r) for x, r in contour]

    # Close to axis for revolve
    pts.insert(0, (pts[0][0], 0.0))
    pts.append((pts[-1][0], 0.0))

    solid = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (1, 0, 0))
    )

    return solid