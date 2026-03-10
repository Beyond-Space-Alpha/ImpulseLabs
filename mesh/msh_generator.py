import gmsh


def generate_axi_mesh(contour, filename="engine_axi.msh"):

    gmsh.initialize()
    gmsh.model.add("rocket_nozzle_axi")

    pts = []

    for x, r in contour:
        p = gmsh.model.geo.addPoint(x, r, 0)
        pts.append(p)

    axis_start = gmsh.model.geo.addPoint(contour[0][0], 0, 0)
    axis_end = gmsh.model.geo.addPoint(contour[-1][0], 0, 0)

    wall_lines = []

    for i in range(len(pts) - 1):
        l = gmsh.model.geo.addLine(pts[i], pts[i + 1])
        wall_lines.append(l)

    inlet = gmsh.model.geo.addLine(axis_start, pts[0])
    outlet = gmsh.model.geo.addLine(pts[-1], axis_end)
    axis = gmsh.model.geo.addLine(axis_end, axis_start)

    loop = gmsh.model.geo.addCurveLoop(
        [inlet] + wall_lines + [outlet, axis]
    )

    surface = gmsh.model.geo.addPlaneSurface([loop])

    gmsh.model.geo.synchronize()

    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.002)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.01)

    gmsh.model.mesh.generate(2)

    gmsh.write(filename)

    gmsh.finalize()

    print("Mesh written to", filename)