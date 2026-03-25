from core.inputs import EngineInputs
from core.engine_solver import run_engine_pipeline
from util.plot import plot_contour
from util.mesh_visualizer import visualize_msh


def ask_float(prompt: str, default: float | None = None) -> float:
    """Read a float from terminal, with optional default."""
    while True:
        raw = input(prompt).strip()

        if raw == "":
            if default is not None:
                return float(default)
            print("Please enter a value.")
            continue

        try:
            return float(raw)
        except ValueError:
            print("Invalid number. Try again.")


def ask_str(prompt: str, default: str | None = None) -> str:
    """Read a string from terminal, with optional default."""
    raw = input(prompt).strip()

    if raw == "" and default is not None:
        return default

    while raw == "":
        print("Please enter a value.")
        raw = input(prompt).strip()

    return raw


def collect_inputs() -> EngineInputs:
    """Collect engine inputs interactively from terminal."""
    print("\n=== ImpulseLabs Backend Test Runner ===")
    print("Press Enter to use the default shown in brackets.\n")

    thrust = ask_float("Thrust [N] [500]: ", 500.0)
    oxidizer = ask_str("Oxidizer [LOX]: ", "LOX")
    fuel = ask_str("Fuel [RP1]: ", "RP1")
    chamber_pressure_bar = ask_float("Chamber pressure [bar] [30]: ", 30.0)
    mixture_ratio = ask_float("Mixture ratio O/F [-] [2.5]: ", 2.5)
    ambient_pressure_bar = ask_float("Ambient pressure [bar] [1.0]: ", 1.0)
    contraction_ratio = ask_float("Contraction ratio rc/rt [-] [3.0]: ", 3.0)

    return EngineInputs(
        thrust=thrust,
        oxidizer=oxidizer,
        fuel=fuel,
        chamber_pressure_bar=chamber_pressure_bar,
        mixture_ratio=mixture_ratio,
        ambient_pressure_bar=ambient_pressure_bar,
        contraction_ratio=contraction_ratio,
    )


def print_solution(solution: dict, mesh_file: str, contour: list[tuple[float, float]]) -> None:
    """Pretty-print the solved engine outputs."""
    inputs = solution["inputs"]

    print("\n================ ENGINE SOLUTION ================\n")
    print(f"Thrust              : {inputs.thrust:.3f} N")
    print(f"Oxidizer            : {inputs.oxidizer}")
    print(f"Fuel                : {inputs.fuel}")
    print(f"Chamber pressure    : {inputs.chamber_pressure_bar:.3f} bar")
    print(f"Ambient pressure    : {inputs.ambient_pressure_bar:.3f} bar")
    print(f"Mixture ratio       : {inputs.mixture_ratio:.3f}")
    print(f"Contraction ratio   : {inputs.contraction_ratio:.3f}")
    print()
    print(f"Tc                  : {solution['Tc']:.3f} K")
    print(f"gamma               : {solution['gamma']:.6f}")
    print(f"cstar               : {solution['cstar']:.3f} m/s")
    print(f"Isp                 : {solution['Isp']:.3f} s")
    print(f"mdot                : {solution['mdot']:.6f} kg/s")
    print(f"Me                  : {solution['Me']:.6f}")
    print(f"Expansion ratio     : {solution['expansion_ratio']:.6f}")
    print(f"At                  : {solution['At']:.8f} m^2")
    print(f"Ae                  : {solution['Ae']:.8f} m^2")
    print(f"rt                  : {solution['rt']:.6f} m")
    print(f"re                  : {solution['re']:.6f} m")
    print(f"rc                  : {solution['rc']:.6f} m")
    print(f"Lc                  : {solution['Lc']:.6f} m")
    print(f"Converging length   : {solution['conv_length']:.6f} m")
    print(f"Mesh file           : {mesh_file}")
    print(f"Contour points      : {len(contour)}")
    print("\n=================================================\n")


def main() -> None:
    try:
        inputs = collect_inputs()
        result = run_engine_pipeline(inputs)

        solution = result["solution"]
        contour = result["contour"]
        mesh_file = result["mesh_file"]

        print_solution(solution, mesh_file, contour)

        plot_contour(contour, show=False)
        visualize_msh(mesh_file, show=False)

        import matplotlib.pyplot as plt
        plt.show()

    except Exception as exc:
        print(f"\nPipeline failed: {exc}")


if __name__ == "__main__":
    main()