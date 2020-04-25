import math
from typing import List, Callable

from projectile.Position import Position
from projectile.forces.CoriolisForce import CoriolisForce
from projectile.forces.DragForce import DragForce
from projectile.forces.EotvosForce import EotvosForce
from projectile.forces.Force import Force
from projectile.forces.NewtonianGravity import NewtonianGravity
from projectile.Projectile import Projectile
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX


R = 8.31447


class Environment:

    """
    Gravity must always be on the same place in the list of forces because other forces (e.g. drag) may depend on it.
    """
    GRAVITY_FORCE_INDEX = 0

    def __init__(self, earth_radius=6378137, earth_angular_velocity=7.292115e-5, std_pressure=101325.0, std_temp=288.15,
                 temp_lapse_rate=lambda h: 0.0065, molar_mass=0.0289654):
        self.earth_radius = earth_radius
        self.earth_angular_velocity = earth_angular_velocity
        self.std_pressure = std_pressure
        self.std_temp = std_temp
        self.temp_lapse_rate = temp_lapse_rate
        self.molar_mass = molar_mass
        self.forces: List[Force] = [NewtonianGravity(), DragForce(), CoriolisForce(), EotvosForce()]

    def add_force(self, force: Force) -> None:
        self.forces.append(force)

    def remove_force(self, force: Force) -> None:
        self.forces.remove(force)

    def density(self, altitude: float) -> float:
        """Works only for troposphere (~18km); temperature lapse rate is by default constant"""
        dummy = Projectile(self, lambda t: 1, [0, 0, 0], Position(0, 0, altitude))
        g = math.fabs(self.forces[Environment.GRAVITY_FORCE_INDEX].get_z(dummy, self))
        return (self.std_pressure * self.molar_mass) / (R * self.std_temp) * \
               (1 - (self.temp_lapse_rate(altitude)*altitude)/self.std_temp) ** \
               (g * self.molar_mass / (R*self.temp_lapse_rate(altitude)) - 1)

    def get_forces_intensity(self, projectile) -> List[float]:
        intensities = [0.0, 0.0, 0.0]
        for force in self.forces:
            intensities[X_INDEX] += force.get_x(projectile, self)
            intensities[Y_INDEX] += force.get_y(projectile, self)
            intensities[Z_INDEX] += force.get_z(projectile, self)
        return intensities

    def create_projectile(self, mass: Callable[[float], float], initial_position: Position, cross_section=lambda: 0.25,
                          drag_coef=lambda: 0.05) -> Projectile:
        return Projectile(self, mass, [0, 0, 0], initial_position, cross_section, drag_coef)
