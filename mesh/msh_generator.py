import gmsh


def generate_mesh(step_file,output_file):

    gmsh.initialize()

    gmsh.model.add("nozzle")

    gmsh.model.occ.importShapes(step_file)

    gmsh.model.occ.synchronize()

    gmsh.model.mesh.generate(3)

    gmsh.write(output_file)

    gmsh.finalize()