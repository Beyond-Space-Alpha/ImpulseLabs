import numpy as np


def converging_parabola(rc, rt, x0, length, n=80):
    """
    Generates a parabolic converging section from chamber to throat.

    Args:
        rc (float): Chamber radius.
        rt (float): Throat radius.
        x0 (float): Starting axial position.
        length (float): Axial length of the converging section.
        n (int): Number of points to generate.

    Returns:
        list: A list of (x, y) coordinates for the converging profile.
    """
    x = np.linspace(x0, x0 + length, n)

    # s is the normalized axial distance (0 to 1)
    s = (x - x0) / length

    # Parabolic profile: y decreases from rc to rt
    # This provides a smooth transition with zero slope at the chamber interface
    y = rc - (rc - rt) * (s**2)

    return list(zip(x, y))
  