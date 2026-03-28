import numpy as np


def throat_fillet(rt, radius=0.02, x0=0, n=40):
    """
    Generates a circular arc fillet for the nozzle throat transition.

    Args:
        rt (float): Throat radius.
        radius (float): Radius of the fillet arc.
        x0 (float): Axial center of the fillet arc.
        n (int): Number of points to generate.

    Returns:
        list: A list of (x, y) coordinates for the circular fillet.
    """
    # Angle spans from -90 degrees (vertical) to 0 degrees (horizontal)
    # to create the transition from the converging section to the throat
    theta = np.linspace(-np.pi / 2, 0, n)

    x = x0 + radius * np.cos(theta)
    y = rt + radius * np.sin(theta)

    return list(zip(x, y))
