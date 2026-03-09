import numpy as np


class RaoMethod:

    def __init__(self, method="simple"):

        self.method = method


    def compute_length(self, rt, re):

        if self.method == "simple":

            conical_length = (re - rt) / np.tan(np.radians(15))

            return 0.8 * conical_length

        raise ValueError("Unknown Rao method")