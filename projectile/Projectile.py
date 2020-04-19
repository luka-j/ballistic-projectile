from __future__ import annotations

from typing import List, TextIO, Callable
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.Position import Position
import numpy as np


class Projectile:
    def __init__(self, environment: Environment, mass: float, initial_velocities: List[float],
                 initial_position: Position, cross_section=lambda: 0.25, drag_coef=lambda: 0.05):
        if initial_position is None:
            initial_position = Position(0, 0, 0)
        self.mass = mass
        self.velocities = np.array(initial_velocities, "float64")
        self.position = initial_position
        self.cross_section = cross_section
        self.drag_coef = drag_coef
        self.environment = environment
        self.directions = np.zeros(3)
        self.time = 0

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
        self.position.x += self.velocities[X_INDEX] * dt
        self.position.y += self.velocities[Y_INDEX] * dt
        self.position.z += self.velocities[Z_INDEX] * dt
        self.time += dt

    def has_hit_ground(self):
        return self.position.z <= 0

    def write_position(self, f: TextIO):
        f.write("{:.4f},{},{},{}\n".format(self.time, self.position.x, self.position.y, self.position.z))
