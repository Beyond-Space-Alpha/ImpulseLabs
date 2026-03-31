"""
Main engine solver: integrates CEA, isentropic flow, and geometry sizing.

Pipeline
--------
EngineInputs
    → validate
    → CEA chamber properties     (Tc, gamma, cstar)
    → isentropic Mach solve      (Me, expansion_ratio)
    → CEA thrust coefficient     (Cf)
    → Isp = cstar * Cf / g0
    → throat sizing              (At)
    → mass flow                  (mdot)
    → chamber + converging sizing
    → contour build
    → mesh generation
    → CAD generation
"""

import numpy as np

from core.validation import validate_inputs
from core.cea_solver import get_combustion_properties, get_cf_from_cea
from core.performance import (
    G0,
    solve_exit_mach,
    area_mach_relation,
    thrust_coefficient_isp,
    throat_area_from_thrust,
    mass_flow_rate_from_pc_at_cstar,
    radius_from_area,
)
from geometry.chamber import chamber_length
from geometry.contour2d import build_full_contour
from mesh.msh_generator import generate_axi_mesh
from cad.nozzle3d import create_3d_nozzle
from cad.step_export import export_step, export_stl

# --- Design constants ---
_L_STAR = 1.0
_THETA_CONV_DEG = 30.0
_BELL_PCT = 80


def solve_engine(inputs):
    """
    Solve full engine thermodynamics and geometry sizing from validated inputs.

    Parameters
    ----------
    inputs : EngineInputs

    Returns
    -------
    dict
        All computed thermodynamic, performance, and geometric parameters.
    """
    validate_inputs(inputs)

    # --- Step 1: chamber properties from CEA ---
    props = get_combustion_properties(inputs)
    gamma = props["gamma"]
    cstar = props["cstar"]
    cea = props["cea"]
    Pc_psi = props["Pc_psi"]

    # --- Step 2: exit Mach and expansion ratio ---
    Me = solve_exit_mach(
        gamma,
        inputs.chamber_pressure_bar,
        inputs.ambient_pressure_bar,
    )
    eps = area_mach_relation(Me, gamma)

    # --- Step 3: thrust coefficient from CEA ---
    Cf = get_cf_from_cea(
        cea=cea,
        Pc_psi=Pc_psi,
        mixture_ratio=inputs.mixture_ratio,
        expansion_ratio=eps,
        ambient_pressure_bar=inputs.ambient_pressure_bar,
    )

    # --- Step 4: Isp from cstar and Cf ---
    Isp = thrust_coefficient_isp(cstar, Cf, G0)

    # --- Step 5: throat area from thrust ---
    Pc_pa = inputs.chamber_pressure_bar * 1e5
    At = throat_area_from_thrust(inputs.thrust, Pc_pa, Cf)
    rt = radius_from_area(At)

    # --- Step 6: mass flow from Pc, At, cstar ---
    mdot = mass_flow_rate_from_pc_at_cstar(Pc_pa, At, cstar)

    # --- Step 7: exit and chamber radii ---
    Ae = eps * At
    re = radius_from_area(Ae)
    rc = inputs.contraction_ratio * rt

    # --- Step 8: converging section geometry ---
    theta_conv = np.radians(_THETA_CONV_DEG)
    conv_length = (rc - rt) / np.tan(theta_conv)

    # --- Step 9: cylindrical chamber length from L* ---
    Lc = chamber_length(
        rt=rt,
        rc=rc,
        L_star=_L_STAR,
        conv_length=conv_length,
    )

    return {
        "inputs": inputs,
        "cea": cea,
        "Tc": props["Tc"],
        "gamma": gamma,
        "cstar": cstar,
        "Cf": Cf,
        "Isp": Isp,
        "mdot": mdot,
        "Me": Me,
        "expansion_ratio": eps,
        "At": At,
        "Ae": Ae,
        "rt": rt,
        "re": re,
        "rc": rc,
        "Lc": Lc,
        "conv_length": conv_length,
    }


def run_engine_pipeline(inputs):
    """
    Full backend pipeline: inputs → solve → contour → mesh → CAD.

    Parameters
    ----------
    inputs : EngineInputs

    Returns
    -------
    dict
        solution  : dict  all engine parameters from solve_engine()
        contour   : list  list of (x, r) tuples for the full nozzle wall
        mesh_file : str   path to the written .msh file
        step_file : str   path to the written .step file
        stl_file  : str   path to the written .stl file
    """
    solution = solve_engine(inputs)

    contour_data = build_full_contour(
        rt=solution["rt"],
        re=solution["re"],
        rc=solution["rc"],
        chamber_length=solution["Lc"],
        conv_length=solution["conv_length"],
        bell_length_percent=_BELL_PCT,
    )

    contour = contour_data["contour"]

    # Keep existing working mesh pipeline untouched
    mesh_file = generate_axi_mesh(
        contour,
        rt=solution["rt"],
        filename="engine_axi.msh",
    )

    # CAD generated from the SAME solved contour
    cad_shape = create_3d_nozzle(contour)
    step_file = export_step(cad_shape, "engine.step")
    stl_file = export_stl(cad_shape, "engine.stl")

    return {
        "solution": solution,
        "contour": contour,
        "mesh_file": mesh_file,
        "step_file": step_file,
        "stl_file": stl_file,
    }