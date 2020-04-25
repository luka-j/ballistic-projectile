from __future__ import annotations

from typing import List, TextIO
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.Position import Position
import numpy as np
from math import cos, sin, pi


class Projectile:
    def __init__(self, environment: Environment, mass: float, initial_velocities: List[float],
                 initial_position: Position, cross_section=lambda: 0.25, drag_coef=lambda: 0.05):
        if initial_position is None:
            initial_position = Position(44.869389, 20.640221, 0)
        self.mass = mass
        self.velocities = np.array(initial_velocities, "float64")
        self.position = initial_position
        self.cross_section = cross_section
        self.drag_coef = drag_coef
        self.environment = environment
        self.directions = np.zeros(3)
        self.time = 0
        self.distance_travelled = 0

    def launch_at_angle(self, pitch: float, yaw: float, velocity: float):
        self.velocities[X_INDEX] = velocity * np.cos(yaw) * np.cos(pitch)
        self.velocities[Y_INDEX] = velocity * np.sin(yaw) * np.cos(pitch)
        self.velocities[Z_INDEX] = velocity * np.sin(pitch)

    def set_initial_velocities(self, vx: float, vy: float, vz: float):
        self.velocities[X_INDEX] = vx
        self.velocities[Y_INDEX] = vy
        self.velocities[Z_INDEX] = vz

    def velocity(self):
        return np.sqrt(np.sum(self.velocities ** 2))

    def advance(self, dt):
        forces = self.environment.get_forces_intensity(self)
        acc = np.divide(forces, self.mass)
        self.velocities += acc * dt
        self.directions = np.sign(self.velocities)

        radius = self.environment.earth_radius+self.position.alt
        dlat = (self.velocities[Y_INDEX]*dt)/radius
        dlon = self.velocities[X_INDEX]/(radius*cos(pi*self.position.lat/180))
        self.position.lat += dlat * 180/pi
        self.position.lon += dlon * 180/pi
        self.position.alt += self.velocities[Z_INDEX] * dt

        self.time += dt
        self.distance_travelled += np.sqrt(np.sum((self.velocities*dt)**2))

    def has_hit_ground(self):
        return self.position.alt <= 0

    def write_position(self, f: TextIO):
        f.write("{:.4f},{:.2f},{},{},{}\n".format(self.time, self.distance_travelled,
                                                  self.position.lat, self.position.lon, self.position.alt))
