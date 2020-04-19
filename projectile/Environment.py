from typing import List

from projectile.Position import Position
from projectile.forces.Force import Force
from projectile.forces.NewtonianGravity import NewtonianGravity
from projectile.forces.SimpleGravity import SimpleGravity
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX


class Environment:
    forces: List[Force] = [NewtonianGravity()]

    def add_force(self, force: Force) -> None:
        self.forces.append(force)

    def remove_force(self, force: Force) -> None:
        self.forces.remove(force)

    def get_forces_intensity(self, projectile) -> List[float]:
        intensities = [0.0, 0.0, 0.0]
        for force in self.forces:
            intensities[X_INDEX] += force.get_x(projectile)
            intensities[Y_INDEX] += force.get_y(projectile)
            intensities[Z_INDEX] += force.get_z(projectile)
        return intensities

    def create_projectile(self, mass: float, initial_position: Position):
        from projectile.Projectile import Projectile
        return Projectile(self, mass, [0, 0, 0], initial_position)
