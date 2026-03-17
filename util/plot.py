import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def plot_contour(contour, show=True):

    x = np.array([p[0] for p in contour])
    y = np.array([p[1] for p in contour])

    fig, ax = plt.subplots(num="Nozzle Contour")

    # nozzle outline
    ax.plot(x, y, linewidth=1.5, color="black")
    ax.plot(x, -y, linewidth=1.5, color="black")

    # closed nozzle polygon
    poly_x = np.concatenate([x, x[::-1], [x[0]]])
    poly_y = np.concatenate([y, -y[::-1], [y[0]]])

    vertices = np.column_stack([poly_x, poly_y])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]

    path = Path(vertices, codes)
    patch = PathPatch(path, facecolor="none", edgecolor="none")
    ax.add_patch(patch)

    # streamwise gradient field
    nx = 1200
    ny = 500

    streamwise = np.linspace(0, 1, nx)
    gradient = np.tile(streamwise, (ny, 1))

    vertical = np.linspace(-1, 1, ny).reshape(ny, 1)
    center_weight = 1.0 - 0.15 * (vertical ** 2)
    field = gradient * center_weight

    # plot limits
    xmin, xmax = x.min(), x.max()
    ymin, ymax = -y.max(), y.max()

    xpad = 0.06 * (xmax - xmin)
    ypad = 0.12 * (ymax - ymin)

    im = ax.imshow(
        field,
        extent=[xmin, xmax, ymin, ymax],
        origin="lower",
        cmap="jet",
        aspect="auto",
        alpha=0.9,
        interpolation="bicubic"
    )

    im.set_clip_path(patch)

    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)

    ax.set_xlabel("x")
    ax.set_ylabel("radius")
    ax.set_title("Nozzle Contour")
    ax.set_aspect("equal")

    if show:
        plt.show()
"""

    x = [p[0] for p in contour]
    y = [p[1] for p in contour]

    plt.figure("Nozzle Contour")
    plt.plot(x, y)
    plt.plot(x, [-v for v in y])

    plt.xlabel("x")
    plt.ylabel("radius")

    plt.title("Nozzle Contour")

    plt.gca().set_aspect("equal")

    if show:
        plt.show()
"""

