from core.inputs import EngineInputs
from core.validation import validate_inputs
from core.cea_solver import get_combustion_properties
from core.performance import *

from geometry.chamber import *
from geometry.converging import *
from geometry.rao import RaoBell
from geometry.contour2d import build_full_contour

from cad.nozzle3d import create_3d_nozzle
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
        Pc=inputs.chamber_pressure_bar*14.5038,
        MR=inputs.mixture_ratio,
        eps=eps
    )

    mdot = inputs.mass_flow or mass_flow_rate(inputs.thrust,Isp)

    At = throat_area(mdot,Pc,cstar)

    rt = diam_from_area(At)/2

    re = rt*(eps**0.5)

    rc = chamber_geometry(rt,inputs.contraction_ratio)

    Lc = chamber_length(rt)

    bell = RaoBell()

    Ln = bell.nozzle_length(rt,re)

        # chamber
    chamber_pts = [
        (-Lc, rc),
        (0, rc)
    ]

    # converging
    conv_pts = converging_section(
        rc,
        rt,
        x_start=0,
        length=0.05
    )

    # bell
    bell_pts = bell.bell_curve(
        rt,
        re,
        Ln,
        x_start=conv_pts[-1][0]
    )

    contour = build_full_contour(
        chamber_pts,
        conv_pts,
        bell_pts
    )

    plot_contour(contour)

    solid = create_3d_nozzle(contour)

    export_step(solid,"engine.step")

    generate_mesh("engine.step","engine.msh")

    print("2D contour + 3D CAD generated")


if __name__=="__main__":
    main()