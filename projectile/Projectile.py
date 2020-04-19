from typing import List

from projectile.Environment import Environment
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
        self.velocities = np.array(initial_velocities)
        self.position = initial_position
        self.environment = environment

    def advance(self, dt):
        forces = self.environment.get_forces_intensity(self)
        acc = np.divide(forces, self.mass)
        self.velocities += acc/dt
        self.position.x += self.velocities[0]*dt
        self.position.y += self.velocities[1]*dt
        self.position.y += self.velocities[2]*dt

    def has_hit_ground(self):
        return self.position.z <= 0
