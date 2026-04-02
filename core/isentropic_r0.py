import numpy as np


def area_mach_relation(m, gamma):
    """
    Calculates the Area-Mach ratio (A/At) for a given Mach number.
    """
    term1 = 1 / m

    # Use spaces around operators and avoid double parentheses where possible
    exponent = (gamma + 1) / (2 * (gamma - 1))
    term2 = ((2 / (gamma + 1)) * (1 + (gamma - 1) / 2 * m**2))**exponent

    return term1 * term2


def characteristic_velocity(gamma, r_gas, tc):
    """
    Calculates the characteristic velocity (c-star).
    """
    term1 = np.sqrt(r_gas * tc)
    
    exponent = (gamma + 1) / (2 * (gamma - 1))
    term2 = gamma * (2 / (gamma + 1))**exponent

    return term1 / term2


def exit_velocity(gamma, r_gas, tc, pe, pc):
    """
    Calculates the theoretical exit velocity.
    """
    return np.sqrt(
        (2 * gamma / (gamma - 1)) * r_gas * tc *
        (1 - (pe / pc)**((gamma - 1) / gamma))
    )