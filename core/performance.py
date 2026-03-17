import numpy as np
from scipy.optimize import fsolve


g0 = 9.80665


def solve_exit_mach(gamma, Pc_bar, Pa_bar):

    Pc = Pc_bar * 1e5
    Pa = Pa_bar * 1e5

    pressure_ratio = Pa / Pc

    def equation(Me):

        return pressure_ratio - (
            1 + (gamma - 1)/2 * Me**2
        )**(-gamma/(gamma-1))

    Me = fsolve(equation, 3)[0]

    return Me


def expansion_ratio(Me, gamma):

    return (1/Me) * (
        (2/(gamma+1)) *
        (1+(gamma-1)/2 * Me**2)
    )**((gamma+1)/(2*(gamma-1)))


def thrust_coefficient(Isp, cstar):

    return (Isp * g0) / cstar


def mass_flow_rate(thrust, Isp):

    return thrust / (Isp * g0)


def throat_area(mdot, Pc, cstar):

    return (mdot * cstar) / Pc


def diam_from_area(A):
    
    return np.sqrt(4*A/np.pi)