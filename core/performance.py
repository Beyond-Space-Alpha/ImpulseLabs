import numpy as np
from scipy.optimize import fsolve


# G0 is a constant, so UPPER_CASE is appropriate
G0 = 9.80665


def solve_exit_mach(gamma, pc_bar, pa_bar):
    """
    Solves for the exit Mach number based on the pressure ratio.
    """
    pc = pc_bar * 1e5
    pa = pa_bar * 1e5

    pressure_ratio = pa / pc

    def equation(me):
        # Added spacing around operators for clarity
        return pressure_ratio - (
            1 + (gamma - 1) / 2 * me**2
        )**(-gamma / (gamma - 1))

    # fsolve returns an array, so [0] extracts the scalar result
    me_result = fsolve(equation, 3)[0]

    return me_result


def expansion_ratio(me, gamma):
    """
    Calculates the area expansion ratio (Ae/At).
    """
    term_a = 1 / me
    term_b = (
        (2 / (gamma + 1)) *
        (1 + (gamma - 1) / 2 * me**2)
    )**((gamma + 1) / (2 * (gamma - 1)))

    return term_a * term_b


def thrust_coefficient(isp, cstar):
    """
    Calculates the thrust coefficient (Cf).
    """
    return (isp * G0) / cstar

def mass_flow_rate(thrust, Isp):

    return thrust / (Isp * g0)


def throat_area(mdot, Pc, cstar):

    return (mdot * cstar) / Pc


def diam_from_area(A):
    
    return np.sqrt(4*A/np.pi)