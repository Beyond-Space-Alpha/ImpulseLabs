import meshio
import matplotlib.pyplot as plt


def visualize_msh(filename, show=True):

    mesh = meshio.read(filename)

    points = mesh.points[:, :2]

    cells = None

    for cell in mesh.cells:
        if cell.type == "triangle":
            cells = cell.data

    plt.figure("2D Axisymmetric Nozzle Mesh")
    plt.triplot(
        points[:, 0],
        points[:, 1],
        cells,
        linewidth=0.5
    )

    plt.xlabel("x")
    plt.ylabel("radius")

    plt.title("2D Axisymmetric Nozzle Mesh")

    plt.gca().set_aspect("equal")

    if show:
        plt.show()