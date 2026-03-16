from core.inputs import EngineInputs
from core.engine_solver import solve_engine
from geometry.contour2d import build_full_contour
from mesh.msh_generator import generate_axi_mesh

from util.plot import plot_contour
from util.mesh_visualizer import visualize_msh


def main():
    inputs = EngineInputs(
        thrust=500.0,
        oxidizer="LOX",
        fuel="RP1",
        chamber_pressure_bar=30.0,
        mixture_ratio=2.5
    )

    solution = solve_engine(inputs)

    contour_data = build_full_contour(
        rt=solution["rt"],
        re=solution["re"],
        rc=solution["rc"],
        chamber_length=solution["Lc"],
        conv_length=solution["conv_length"]
    )

    contour = contour_data["contour"]

    plot_contour(contour)
    generate_axi_mesh(contour)
    visualize_msh("engine_axi.msh")


if __name__ == "__main__":
    main()