"""User supplied design inputs for the ImpulseLabs engine solver."""
from dataclasses import dataclass
@dataclass
class EngineInputs:
     """
    All user defined parameters required to run the engine pipeline.

    Required
    --------
    thrust              : Engine thrust [N]
    oxidizer            : Oxidizer name recognised by RocketCEA (e.g. 'LOX')
    fuel                : Fuel name recognised by RocketCEA (e.g. 'RP1')
    chamber_pressure_bar: Chamber pressure [bar]
    mixture_ratio       : Oxidizer-to-fuel mass ratio [-]

    Optional
    --------------------------------------
    ambient_pressure_bar: Ambient pressure at nozzle exit[bar]
    contraction_ratio   : Chamber-to-throat area ratio Ac/At [-]
    mass_flow           : Optional mass flow override [kg/s]
    """
    #---required---
     thrust: float
     oxidizer: str
     fuel: str
     chamber_pressure_bar: float
     mixture_ratio: float

     #---optional---

     ambient_pressure_bar: float = 1.0
     contraction_ratio: float = 3.0
     mass_flow: float | None = None
