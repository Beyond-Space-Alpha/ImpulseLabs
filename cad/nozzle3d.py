import cadquery as cq


def clean_points(points):

    clean=[]

    for p in points:
        if len(clean)==0 or p!=clean[-1]:
            clean.append(p)

    return clean


def create_3d_nozzle(contour):

    contour = clean_points(contour)

    pts=[(x,y) for x,y in contour]

    pts.insert(0,(pts[0][0],0))
    pts.append((pts[-1][0],0))

    wp=cq.Workplane("XZ")

    solid=(
        wp.polyline(pts)
        .close()
        .revolve(360,(0,0,0),(1,0,0))
    )

    return solid