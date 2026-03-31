import cadquery as cq


def clean_points(points):
    """
    Removes consecutive duplicate points from a list.
    """
    clean = []

    for p in points:
        if not clean or p != clean[-1]:
            clean.append(p)

    return clean


def create_3d_nozzle(contour):
    """
    Creates a 3D nozzle solid by revolving a 2D contour around the X-axis.
    """
    contour = clean_points(contour)

    # x and y represent the propulsion coordinate standards
    pts = [(x, y) for x, y in contour]

    # Insert boundary points for the revolution face
    pts.insert(0, (pts[0][0], 0))
    pts.append((pts[-1][0], 0))

    # Construct the workplane and revolve
    wp = cq.Workplane("XZ")

    solid = (
        wp.polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (1, 0, 0))
    )

    return solid