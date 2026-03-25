"""Isentropic flow relations and rocket performance calculations."""

import numpy as np
from scipy.optimize import brentq

G0 = 9.80665 #standard gravity [m/s^2]

def solve_exit_mach(gamma: float, Pc_bar: float, Pa_bar: float)-> float:
    """
    Solves for the exit Mach number of the nozzle flow using isentropic flow relations.
    Uses Brent's method on a bounded interval [1.001, 50] to find the root of the equation relating pressure ratio to Mach number.
    Guarantees convergence for all practical chamber-to-ambient pressure ratios.
    
    Parameters
    ----------
    gamma : float Ratio of specific heats at chamber conditions [-]
    Pc_bar : float Chamber pressure [bar]
    Pa_bar : float Ambient pressure [bar]
    
    Returns
    -------
    Me : float Exit Mach number [-]
    """

    pressure_ratio = Pa_bar / Pc_bar

    def _residual(Me: float)-> float:
        return(
            (1.0 + (gamma - 1.0)/2.0 * Me**2)**(-gamma/(gamma-1.0)) 
            - pressure_ratio
        )

    Me = brentq(_residual, 1.001, 50, xtol=1e-8)
    return float(Me)

def area_mach_relation(Me: float, gamma: float)-> float:
    """
    Computes the area ratio (Ae/At) from the exit Mach number.
    Parameters
    ----------
    Me : float Exit Mach number [-]
    gamma : float Ratio of specific heats at chamber conditions [-]
    Returns
    -------
    eps : float Expansion ratio (Ae/At) [-]
    """
    term = (2.0/(gamma+1.0)) * (
        1.0 + (gamma-1.0)/2.0 * Me**2)
    
    return (1.0/Me) * term **(
        (gamma+1.0)/(2.0*(gamma-1.0))
    )

def mass_flow_rate(thrust: float, Isp: float)-> float:
    """
    Computes propellant mass flow rate from the thrust and specific impulse.
    Parameters
    ----------
    thrust : float Engine thrust [N]
    Isp : float Specific impulse [s]
    Returns
    -------
    mdot : float Propellant mass flow rate [kg/s]
    """
    return thrust / (Isp * G0)

def throat_area(mdot: float, Pc_pa: float, cstar: float)-> float:
    """
    Computes nozzle throat area from the continuity equation
    Parameters
    ----------
    mdot : float Propellant mass flow rate [kg/s]
    Pc_pa : float Chamber pressure [Pa]
    cstar : float Characteristic velocity [m/s]
    Returns
    -------
    At : float Throat area [m^2]
    """
    return (mdot * cstar) / Pc_pa


def radius_from_area(area: float)-> float:
    """Computes the radius of a circle given its area."""
    
    return np.sqrt(area/np.pi)