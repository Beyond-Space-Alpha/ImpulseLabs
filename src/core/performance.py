"""Isentropic flow relations and rocket performance calculations."""

import numpy as np
from scipy.optimize import brentq

G0 = 9.80665  # standard gravity [m/s^2]


def solve_exit_mach(gamma: float, Pc_bar: float, Pa_bar: float) -> float:
    """
    Solves for exit Mach number from chamber-to-ambient pressure ratio.
    """
    pressure_ratio = Pa_bar / Pc_bar

    def _residual(Me: float) -> float:
        return (
            (1.0 + (gamma - 1.0) / 2.0 * Me**2) ** (-gamma / (gamma - 1.0))
            - pressure_ratio
        )

    Me = brentq(_residual, 1.001, 50.0, xtol=1e-8)
    return float(Me)


def area_mach_relation(Me: float, gamma: float) -> float:
    """
    Computes area ratio Ae/At from exit Mach number.
    """
    term = (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * Me**2)
    return (1.0 / Me) * term ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))


def thrust_coefficient_isp(cstar: float, cf: float, g0: float = G0) -> float:
    """
    Computes specific impulse from cstar and thrust coefficient.

    Isp = cstar * Cf / g0
    """
    return (cstar * cf) / g0


def throat_area_from_thrust(thrust: float, Pc_pa: float, cf: float) -> float:
    """
    Computes throat area from thrust coefficient relation.

    At = Thrust / (Pc * Cf)
    """
    return thrust / (Pc_pa * cf)


def mass_flow_rate_from_pc_at_cstar(Pc_pa: float, At: float, cstar: float) -> float:
    """
    Computes mass flow rate from cstar definition.

    mdot = Pc * At / cstar
    """
    return (Pc_pa * At) / cstar


def radius_from_area(area: float) -> float:
    """
    Computes the radius of a circle from its area.
    """
    return np.sqrt(area / np.pi)