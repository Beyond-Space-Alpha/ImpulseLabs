from dataclasses import dataclass


@dataclass
class EngineInputs:
    """
    Container for rocket engine design parameters.
    """

    thrust: float
    oxidizer: str
    fuel: str

    chamber_pressure_bar: float
    mixture_ratio: float

    ambient_pressure_bar: float = 1.0
    contraction_ratio: float = 3.0
    mass_flow: float | None = None