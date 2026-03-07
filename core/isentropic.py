import numpy as np

def area_mach_relation(M, gamma):

    term1 = 1/M

    term2 = ((2/(gamma+1))*(1+(gamma-1)/2*M**2))**((gamma+1)/(2*(gamma-1)))

    return term1*term2


def characteristic_velocity(gamma, R, Tc):

    term1 = np.sqrt(R*Tc)

    term2 = gamma*(2/(gamma+1))**((gamma+1)/(2*(gamma-1)))

    return term1/term2


def exit_velocity(gamma, R, Tc, Pe, Pc):

    return np.sqrt(
        (2*gamma/(gamma-1)) * R * Tc *
        (1 - (Pe/Pc)**((gamma-1)/gamma))
    )