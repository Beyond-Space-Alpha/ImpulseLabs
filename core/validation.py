"""Input validation for EngineInputs."""


def validate_inputs(inputs) -> None:
    """Validate all fields of an EngineInputs instance."""

    if inputs.thrust <= 0.0:
        raise ValueError(f"Thrust must be positive, got {inputs.thrust} N.")

    if inputs.chamber_pressure_bar <= 0.0:
        raise ValueError(f"Chamber pressure must be positive, got {inputs.chamber_pressure_bar} bar.")

    if inputs.ambient_pressure_bar <= 0.0:
        raise ValueError(f"Ambient pressure must be positive, got {inputs.ambient_pressure_bar} bar.")

    if inputs.chamber_pressure_bar <= inputs.ambient_pressure_bar:
        raise ValueError(
            "Chamber pressure must exceed ambient pressure for a supersonic nozzle. "
            f"Got Pc={inputs.chamber_pressure_bar} bar, Pa={inputs.ambient_pressure_bar} bar."
        )

    if inputs.mixture_ratio <= 0.0:
        raise ValueError(f"Mixture ratio must be positive, got {inputs.mixture_ratio}.")

    if inputs.contraction_ratio < 1.0:
        raise ValueError(f"Contraction ratio must be >= 1, got {inputs.contraction_ratio}.")

    if inputs.mass_flow is not None and inputs.mass_flow <= 0.0:
        raise ValueError(f"Mass flow override must be positive, got {inputs.mass_flow} kg/s.")

