import numpy as np


class Position:
    def __init__(self, lat, lon, alt):
        # this is CRUCIAL - forces such as Coriolis generate pretty small movement which is lost as a rounding error
        # when doing operations with position
        data = np.array([lat, lon, alt], "float128")
        self.lat = data[0]
        self.lon = data[1]
        self.alt = data[2]
