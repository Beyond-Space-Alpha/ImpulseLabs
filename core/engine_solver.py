"""
Main engine solver: integrates CEA, isentropic flow, and geometry sizing.

Pipeline
--------
EngineInputs
    → validate
    → CEA combustion properties  (Tc, gamma, cstar)
    → isentropic Mach solve      (Me, expansion_ratio)
    → CEA Isp at expansion ratio (Isp)
    → mass flow + throat sizing  (mdot, At, rt)
    → chamber + converging sizing (rc, Lc, conv_length)
"""

import numpy as np

from core.validation import validate_inputs
from core.cea_solver import get_combustion_properties, get_isp_from_cea
from core.performance import (
    solve_exit_mach,
    area_mach_relation,
    mass_flow_rate,
    throat_area,
    radius_from_area,
)
from geometry.chamber import chamber_length
from geometry.contour2d import build_full_contour
from mesh.msh_generator import generate_axi_mesh

# --- Design constants ---
_L_STAR = 1.0           # characteristic chamber length [m]
_THETA_CONV_DEG = 30.0  # converging half-angle [deg]
_BELL_PCT = 80          # Rao bell length percentage (60, 80, or 90)


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

    # --- Step 1: CEA combustion properties ---
    props = get_combustion_properties(inputs)
    gamma = props["gamma"]
    cstar = props["cstar"]
    cea = props["cea"]
    Pc_psi = props["Pc_psi"]

    # --- Step 2: Isentropic exit conditions ---
    Me = solve_exit_mach(gamma, inputs.chamber_pressure_bar, inputs.ambient_pressure_bar)
    eps = area_mach_relation(Me, gamma)

    # --- Step 3: Isp from CEA at computed expansion ratio ---
    Isp = get_isp_from_cea(cea, Pc_psi, inputs.mixture_ratio, eps)

    # --- Step 4: Mass flow and throat sizing ---
    mdot = mass_flow_rate(inputs.thrust, Isp)
    Pc_pa = inputs.chamber_pressure_bar * 1e5
    At = throat_area(mdot, Pc_pa, cstar)
    rt = radius_from_area(At)

    # --- Step 5: Exit and chamber radii ---
    Ae = eps * At
    re = radius_from_area(Ae)
    rc = inputs.contraction_ratio * rt

    # --- Step 6: Converging section geometry ---
    theta_conv = np.radians(_THETA_CONV_DEG)
    conv_length = (rc - rt) / np.tan(theta_conv)

    # --- Step 7: Cylindrical chamber length from L* ---
    Lc = chamber_length(
        rt=rt,
        rc=rc,
        L_star=_L_STAR,
        conv_length=conv_length,
    )

    return {
        "inputs": inputs,
        "cea": props["cea"],
        "Tc": props["Tc"],
        "gamma": gamma,
        "cstar": cstar,
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
    Full backend pipeline: inputs → solve → contour → mesh.

    Parameters
    ----------
    inputs : EngineInputs

    Returns
    -------
    dict
        solution  : dict  all engine parameters from solve_engine()
        contour   : list  list of (x, r) tuples for the full nozzle wall
        mesh_file : str   path to the written .msh file
    """

    solution = solve_engine(inputs)

    contour_data = build_full_contour(
        rt=solution["rt"],
        re=solution["re"],
        rc=solution["rc"],
        chamber_length=solution["Lc"],
        conv_length=solution["conv_length"],
    )

    contour = contour_data["contour"]

    mesh_file = generate_axi_mesh(contour, rt=solution["rt"], filename="engine_axi.msh")
 

    return {
        "solution": solution,
        "contour": contour,
        "mesh_file": mesh_file,
    }