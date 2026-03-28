import gmsh
import numpy as np


def clean_contour(contour):
    """
    Removes duplicates and ensures the contour progresses logically for meshing.
    """
    clean = []

    for p in contour:
        if not clean:
            clean.append(p)
            continue

        # Remove duplicate points using a small tolerance
        if np.allclose(p, clean[-1], atol=1e-8):
            continue

        # Enforce increasing x-coordinates to prevent self-intersecting loops
        if p[0] < clean[-1][0]:
            continue

        clean.append(p)

    return clean


def generate_axi_mesh(contour, filename="engine_axi.msh"):
    """
    Generates a 2D axisymmetric mesh for a rocket nozzle using Gmsh.

    Args:
        contour (list): List of (x, r) tuples defining the nozzle wall.
        filename (str): Output path for the .msh file.
    """
    contour = clean_contour(contour)

    gmsh.initialize()
    gmsh.model.add("rocket_nozzle")

    # Define points along the nozzle wall
    # We use a characteristic length of 0.002 as a default refinement
    pts = []
    for x, r in contour:
        pts.append(
            gmsh.model.geo.addPoint(x, r, 0, 0.002)
        )

    # Define points along the symmetry axis (r=0)
    axis_start = gmsh.model.geo.addPoint(contour[0][0], 0, 0)
    axis_end = gmsh.model.geo.addPoint(contour[-1][0], 0, 0)

    # Create the nozzle wall segments
    wall_lines = []
    for i in range(len(pts) - 1):
        wall_lines.append(
            gmsh.model.geo.addLine(pts[i], pts[i + 1])
        )

    # Close the domain: Inlet, Outlet, and Symmetry Axis
    inlet = gmsh.model.geo.addLine(axis_start, pts[0])
    outlet = gmsh.model.geo.addLine(pts[-1], axis_end)
    axis = gmsh.model.geo.addLine(axis_end, axis_start)

    # Define the surface for meshing
    curve_loop = gmsh.model.geo.addCurveLoop(
        [inlet] + wall_lines + [outlet, axis]
    )
    gmsh.model.geo.addPlaneSurface([curve_loop])

    gmsh.model.geo.synchronize()

    # Mesh size controls: global constraints for element size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.001)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.01)

    # Generate 2D triangular mesh
    gmsh.model.mesh.generate(2)

    gmsh.write(filename)
    gmsh.finalize()

    print(f"Mesh successfully written to: {filename}")