import meshio
import pyvista as pv
import numpy as np

mesh = meshio.read("nozzle.msh")

points = mesh.points
triangles = mesh.cells_dict["triangle"]

faces = np.hstack([np.full((len(triangles),1),3), triangles]).flatten()

poly = pv.PolyData(points, faces)

poly.plot(show_edges=True)