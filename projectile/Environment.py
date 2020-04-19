from typing import List

from projectile.Position import Position
from projectile.forces.DragForce import DragForce
from projectile.forces.Force import Force
from projectile.forces.NewtonianGravity import NewtonianGravity
from projectile.Projectile import Projectile
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX


R = 8.31447


class Environment:
    std_pressure = 101325.0
    std_temp = 288.15
    gravity_acc = 9.80665
    # gravity acceleration can also be calculated (depends on height, distance from center of mass-see NewtonianGravity)
    temp_lapse_rate = 0.0065
    molar_mass = 0.0289654

    forces: List[Force] = [NewtonianGravity(), DragForce()]

    def add_force(self, force: Force) -> None:
        self.forces.append(force)

    def remove_force(self, force: Force) -> None:
        self.forces.remove(force)

    def density(self, altitude: float) -> float:
        """Works only for troposphere (~18km), uses const g"""
        return (self.std_pressure * self.molar_mass) / (R * self.std_temp) * \
               (1 - (self.temp_lapse_rate*altitude)/self.std_temp) ** \
               (self.gravity_acc * self.molar_mass / (R*self.temp_lapse_rate) - 1)

    def get_forces_intensity(self, projectile) -> List[float]:
        intensities = [0.0, 0.0, 0.0]
        for force in self.forces:
            intensities[X_INDEX] += force.get_x(projectile, self)
            intensities[Y_INDEX] += force.get_y(projectile, self)
            intensities[Z_INDEX] += force.get_z(projectile, self)
        return intensities

    def create_projectile(self, mass: float, initial_position: Position, cross_section=lambda: 0.25,
                          drag_coef=lambda: 0.05) -> Projectile:
        return Projectile(self, mass, [0, 0, 0], initial_position, cross_section, drag_coef)
