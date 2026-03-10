import matplotlib.pyplot as plt


def plot_contour(contour):

    x = [p[0] for p in contour]
    y = [p[1] for p in contour]

    plt.plot(x, y)
    plt.plot(x, [-v for v in y])

    plt.xlabel("x")
    plt.ylabel("radius")

    plt.title("Nozzle Contour")

    plt.gca().set_aspect("equal")

    plt.show()