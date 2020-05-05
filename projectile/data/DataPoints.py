import numpy as np


class ProjectileDataPoint:
    def __init__(self, time: float, planar_distance: float, latitude: float, longitude: float, altitude: float,
                 x_speed: float, y_speed: float, z_speed: float, pitch: float, yaw: float, remaining_fuel: float):
        self.time = time
        self.planar_distance = planar_distance
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.z_speed = z_speed
        self.pitch = pitch
        self.yaw = yaw
        self.remaining_fuel = remaining_fuel


class ForcesDataPoint:
    def __init__(self, time: float, mass: float, forces_matrix: np.ndarray):
        self.time = time
        self.mass = mass
        self.forces = forces_matrix
