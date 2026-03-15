from geometry.chamber import chamber_length
from geometry.rao import RaoBell
from mesh.msh_generator import generate_axi_mesh

from util.plot import plot_contour
from util.mesh_visualizer import visualize_msh


def main():

    # Example geometry (normally computed from RocketCEA)
    rt = 0.02
    re = 0.06
    chamber_radius = 0.04

    # converging section geometry
    conv_start_x = 0.0
    conv_end_x = 0.02
    conv_length = conv_end_x - conv_start_x

    # compute chamber length instead of fixing it
    chamber_len = chamber_length(rt, chamber_radius, L_star=1.0, conv_length=conv_length)

    # chamber section
    chamber = [
        (-chamber_len, chamber_radius),
        (0, chamber_radius)
    ]

    # converging
    converging = [
        (0, chamber_radius),
        (0.02, rt)
    ]

    # bell nozzle
    rao = RaoBell()

    L = rao.length(rt, re)

    bell = rao.contour(rt, re, L, x0=0.02)

    contour = chamber + converging + bell

    # show contour
    plot_contour(contour)

    # generate mesh
    generate_axi_mesh(contour)

    # visualize mesh
    visualize_msh("engine_axi.msh")


if __name__ == "__main__":
    main()