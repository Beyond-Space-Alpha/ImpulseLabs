import cadquery as cq


def create_nozzle(contour):

    points = [(x, y) for x, y in contour]

    points.insert(0, (0, 0))
    points.append((contour[-1][0], 0))

    wp = cq.Workplane("XZ")

    nozzle = (
        wp.polyline(points)
        .close()
        .revolve(360, (0,0,0), (1,0,0))
    )

    return nozzle