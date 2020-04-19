from typing import List

from projectile.Position import Position
from projectile.Projectile import Projectile
from projectile.forces.Force import Force
from projectile.forces.NormalGravity import NormalGravity


class Environment:
    forces: List[Force] = [NormalGravity()]

    def add_force(self, force: Force) -> None:
        self.forces.append(force)

    def remove_force(self, force: Force) -> None:
        self.forces.remove(force)

    def get_forces_intensity(self, projectile: Projectile) -> List[float]:
        intensities = [0, 0, 0]
        for force in self.forces:
            intensities[0] += force.get_x(projectile)
            intensities[1] += force.get_y(projectile)
            intensities[2] += force.get_z(projectile)
        return intensities

    def create_projectile(self, mass: float, initial_position: Position) -> Projectile:
        return Projectile(self, mass, [0, 0, 0], initial_position)
