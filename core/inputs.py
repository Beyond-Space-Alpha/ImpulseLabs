from dataclasses import dataclass

@dataclass
class EngineInputs:

    chamber_pressure: float
    chamber_temperature: float
    gamma: float
    gas_constant: float
    exit_pressure: float
    thrust: float