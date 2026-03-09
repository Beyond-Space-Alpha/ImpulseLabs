def validate_inputs(inputs):

    if inputs.thrust <= 0:
        raise ValueError("Thrust must be positive")

    if inputs.chamber_pressure_bar <= 0:
        raise ValueError("Chamber pressure must be positive")

    if inputs.mixture_ratio <= 0:
        raise ValueError("Mixture ratio must be positive")

    if inputs.contraction_ratio < 1:
        raise ValueError("Contraction ratio must be > 1")

    return True