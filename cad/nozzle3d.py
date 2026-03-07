import cadquery as cq


def create_nozzle(contour):

    wp=cq.Workplane("XZ")

    wp=wp.polyline(contour)

    nozzle=wp.revolve(360)

    return nozzle