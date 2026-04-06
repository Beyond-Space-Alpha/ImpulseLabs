"""ImpulseLabs — command-line entry point for the engine pipeline."""

from core.inputs import EngineInputs
from core.engine_solver import run_engine_pipeline
from util.plot import plot_contour
from util.mesh_visualizer import visualize_msh

import matplotlib.pyplot as plt


# --- Hardcoded design point (LOX/RP1, 30 bar, 500 N) ---
_DEFAULT_INPUTS = EngineInputs(
    thrust=1000.0,
    oxidizer="LOX",
    fuel="RP1",
    chamber_pressure_bar=40.0,
    mixture_ratio=2.5,
    ambient_pressure_bar=1.0,
    contraction_ratio=3.0,
)


def _print_solution(solution: dict, mesh_file: str, contour: list) -> None:
    """Pretty-print solved engine outputs to stdout."""
    inp = solution["inputs"]

    print("\n================ ENGINE SOLUTION ================\n")
    print(f"  Thrust              : {inp.thrust:.3f} N")
    print(f"  Oxidizer            : {inp.oxidizer}")
    print(f"  Fuel                : {inp.fuel}")
    print(f"  Chamber pressure    : {inp.chamber_pressure_bar:.3f} bar")
    print(f"  Ambient pressure    : {inp.ambient_pressure_bar:.3f} bar")
    print(f"  Mixture ratio       : {inp.mixture_ratio:.3f}")
    print(f"  Contraction ratio   : {inp.contraction_ratio:.3f}")
    print()
    print(f"  Tc                  : {solution['Tc']:.3f} K")
    print(f"  gamma               : {solution['gamma']:.6f}")
    print(f"  cstar               : {solution['cstar']:.3f} m/s")
    print(f"  Cf                  : {solution['Cf']:.6f}")
    print(f"  Isp                 : {solution['Isp']:.3f} s")
    print(f"  mdot                : {solution['mdot']:.6f} kg/s")
    print(f"  Me                  : {solution['Me']:.6f}")
    print(f"  Expansion ratio     : {solution['expansion_ratio']:.6f}")
    print(f"  At                  : {solution['At']:.8f} m^2")
    print(f"  Ae                  : {solution['Ae']:.8f} m^2")
    print(f"  rt                  : {solution['rt']:.6f} m")
    print(f"  re                  : {solution['re']:.6f} m")
    print(f"  rc                  : {solution['rc']:.6f} m")
    print(f"  Lc                  : {solution['Lc']:.6f} m")
    print(f"  Converging length   : {solution['conv_length']:.6f} m")
    print(f"  Mesh file           : {mesh_file}")
    print(f"  Contour points      : {len(contour)}")
    print("\n=================================================\n")


def main() -> None:
    """Run the full engine pipeline and display contour and mesh plots."""
    try:
        result = run_engine_pipeline(_DEFAULT_INPUTS)

        _print_solution(result["solution"], result["mesh_file"], result["contour"])

        plot_contour(result["contour"], show=False)
        visualize_msh(result["mesh_file"], show=False)

        plt.show()

    except Exception as exc:
        print(f"\nPipeline failed: {exc}")
        raise


if __name__ == "__main__":
    main()