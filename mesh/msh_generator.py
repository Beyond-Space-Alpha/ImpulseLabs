import gmsh
import numpy as np


def clean_contour(contour):
    clean = []

    for p in contour:
        if len(clean) == 0:
            clean.append(p)
            continue

        if np.allclose(p, clean[-1]):
            continue

        if p[0] <= clean[-1][0]:
            continue

        clean.append(p)

    return clean


def generate_axi_mesh(contour, rt=None, filename="engine_axi.msh"):
    contour = clean_contour(contour)

    gmsh.initialize()
    gmsh.model.add("rocket_nozzle")

    try:
        pts = []

        for x, r in contour:
            pts.append(
                gmsh.model.geo.addPoint(x, r, 0, 0.002)
            )

        axis_start = gmsh.model.geo.addPoint(contour[0][0], 0, 0)
        axis_end = gmsh.model.geo.addPoint(contour[-1][0], 0, 0)

        wall = []

        for i in range(len(pts) - 1):
            wall.append(
                gmsh.model.geo.addLine(pts[i], pts[i + 1])
            )

        inlet = gmsh.model.geo.addLine(axis_start, pts[0])
        outlet = gmsh.model.geo.addLine(pts[-1], axis_end)
        axis = gmsh.model.geo.addLine(axis_end, axis_start)

        loop = gmsh.model.geo.addCurveLoop(
            [inlet] + wall + [outlet, axis]
        )

        gmsh.model.geo.addPlaneSurface([loop])
        gmsh.model.geo.synchronize()

        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.001)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.01)

        gmsh.model.mesh.generate(2)
        gmsh.write(filename)

        print("Mesh written:", filename)
        return filename

    finally:
        gmsh.finalize()
