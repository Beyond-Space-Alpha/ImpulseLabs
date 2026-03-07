import numpy as np
from .isentropic import characteristic_velocity


def throat_area(thrust, Pc, Cf):

    return thrust/(Pc*Cf)


def thrust_coefficient(gamma, Pe, Pc, Ae_At):

    term1 = np.sqrt(
        (2*gamma**2/(gamma-1)) *
        (2/(gamma+1))**((gamma+1)/(gamma-1)) *
        (1-(Pe/Pc)**((gamma-1)/gamma))
    )

    term2 = (Pe/Pc)*Ae_At

    return term1+term2


def expansion_ratio(Me, gamma):

    return (1/Me) * ((2/(gamma+1)*(1+(gamma-1)/2*Me**2))**((gamma+1)/(2*(gamma-1))))


def compute_performance(inputs):

    Pc = inputs.chamber_pressure
    Tc = inputs.chamber_temperature
    gamma = inputs.gamma
    R = inputs.gas_constant
    Pe = inputs.exit_pressure

    Me = 3.0

    Ae_At = expansion_ratio(Me,gamma)

    Cf = thrust_coefficient(gamma,Pe,Pc,Ae_At)

    At = throat_area(inputs.thrust,Pc,Cf)

    rt = np.sqrt(At/np.pi)

    re = rt*np.sqrt(Ae_At)

    return {
        "Cf":Cf,
        "Ae_At":Ae_At,
        "At":At,
        "rt":rt,
        "re":re
    }