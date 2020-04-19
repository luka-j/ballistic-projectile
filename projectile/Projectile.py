from __future__ import annotations

from typing import List, TextIO
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.Position import Position
import numpy as np


class Projectile:
    velocities: np.array
    environment: Environment
    position: Position
    mass: float

    def __init__(self, environment: Environment, mass: float, initial_velocities: List[float], initial_position=None):
        if initial_position is None:
            initial_position = Position(0, 0, 0)
        self.mass = mass
        self.velocities = np.array(initial_velocities, "float64")
        self.position = initial_position
        self.environment = environment

    def launch_at_angle(self, pitch: float, yaw: float, velocity: float):
        self.velocities[X_INDEX] = velocity * np.cos(yaw) * np.cos(pitch)
        self.velocities[Y_INDEX] = velocity * np.sin(yaw) * np.cos(pitch)
        self.velocities[Z_INDEX] = velocity * np.sin(pitch)

    def set_initial_velocities(self, vx: float, vy: float, vz: float):
        self.velocities[X_INDEX] = vx
        self.velocities[Y_INDEX] = vy
        self.velocities[Z_INDEX] = vz

    def advance(self, dt):
        forces = self.environment.get_forces_intensity(self)
        acc = np.divide(forces, self.mass)
        self.velocities += acc*dt
        self.position.x += self.velocities[X_INDEX]*dt
        self.position.y += self.velocities[Y_INDEX]*dt
        self.position.z += self.velocities[Z_INDEX]*dt

    def has_hit_ground(self):
        return self.position.z <= 0

    def write_position(self, f: TextIO):
        f.write("{},{},{}\n".format(self.position.x, self.position.y, self.position.z))
