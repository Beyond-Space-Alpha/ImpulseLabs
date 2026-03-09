from core.inputs import EngineInputs
from core.validation import validate_inputs
from core.cea_solver import get_combustion_properties
from core.performance import *

from geometry.rao import RaoMethod
from geometry.contour import generate_contour
from geometry.chamber import *

from cad.nozzle3d import create_nozzle
from cad.step_export import export_step

from mesh.msh_generator import generate_mesh
from util.plot import plot_contour


def main():

    inputs = EngineInputs(

        thrust=500,
        oxidizer="LOX",
        fuel="RP-1",

        chamber_pressure_bar=30,
        mixture_ratio=2.5
    )

    validate_inputs(inputs)

    cea_data = get_combustion_properties(inputs)

    gamma = cea_data["gamma"]
    cstar = cea_data["cstar"]
    cea = cea_data["cea"]

    Me = solve_exit_mach(
        gamma,
        inputs.chamber_pressure_bar,
        inputs.ambient_pressure_bar
    )

    eps = expansion_ratio(Me, gamma)

    Pc = inputs.chamber_pressure_bar * 1e5

    Isp = cea.get_Isp(
        Pc=inputs.chamber_pressure_bar * 14.5038,
        MR=inputs.mixture_ratio,
        eps=eps
    )

    Cf = thrust_coefficient(Isp, cstar)

    mdot = inputs.mass_flow or mass_flow_rate(inputs.thrust, Isp)

    At = throat_area(mdot, Pc, cstar)

    rt = diam_from_area(At) / 2

    re = rt * (eps**0.5)

    rc = chamber_geometry(rt, inputs.contraction_ratio)

    Lc = chamber_length(rt)

    print("\nRESULTS\n")

    print("Exit Mach:", Me)
    print("Expansion Ratio:", eps)
    print("Isp:", Isp)
    print("Mass Flow:", mdot)

    print("Throat Radius:", rt)
    print("Exit Radius:", re)
    print("Chamber Radius:", rc)
    print("Chamber Length:", Lc)

    rao = RaoMethod()

    Ln = rao.compute_length(rt, re)

    contour = generate_contour(rt, re, Ln)

    plot_contour(contour)

    nozzle = create_nozzle(contour)

    export_step(nozzle, "nozzle.step")

    generate_mesh("nozzle.step", "nozzle.msh")

    print("\nSTEP + MESH GENERATED")


if __name__ == "__main__":

    main()