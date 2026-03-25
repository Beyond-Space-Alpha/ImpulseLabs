from core.engine_solver import run_engine_pipeline
from util.plot import plot_contour
from util.mesh_visualizer import visualize_msh
from core.inputs import EngineInputs


def main():
    inputs = EngineInputs(
        thrust=500.0,
        oxidizer="LOX",
        fuel="RP1",
        chamber_pressure_bar=30.0,
        mixture_ratio=2.5
    )

    """

    solution = solve_engine(inputs)

    contour_data = build_full_contour(
        rt=solution["rt"],
        re=solution["re"],
        rc=solution["rc"],
        chamber_length=solution["Lc"],
        conv_length=solution["conv_length"]
    )

    contour = chamber + converging + bell

    # show contour
    plot_contour(contour)

    # generate mesh
    generate_axi_mesh(contour)
    visualize_msh("engine_axi.msh", show=False)
    """

    result = run_engine_pipeline(inputs)
    contour = result["contour"]
    plot_contour(contour)
    visualize_msh(result["mesh_file"])

    # visualize mesh
    visualize_msh("engine_axi.msh")


if __name__ == "__main__":
    main()