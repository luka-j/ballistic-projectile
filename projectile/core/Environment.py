from math import exp
from typing import List

import numpy as np

from projectile.core.Constants import DEBUG, R, StandardAtmosphere
from projectile.core.Position import Position
from projectile.core.Projectile import Projectile
from projectile.data.CsvReaders import ForcesCsvReader
from projectile.forces.CentrifugalForce import CentrifugalForce
from projectile.forces.CoriolisForce import CoriolisForce
from projectile.forces.DragForce import DragForce
from projectile.forces.EotvosForce import EotvosForce
from projectile.forces.Force import Force
from projectile.forces.NewtonianGravity import NewtonianGravity
from projectile.data.Plotter import simple_force_plot


class Environment:

    def __init__(self, earth_radius=6378137, earth_angular_velocity=7.2921159e-5, surface_altitude=lambda pos: 0,
                 std_gravity_acc=9.80665, atmosphere=StandardAtmosphere()):
        self.earth_radius = earth_radius
        self.earth_angular_velocity = earth_angular_velocity
        self.surface_altitude = surface_altitude
        self.std_gravity = std_gravity_acc
        self.atmosphere = atmosphere
        self.forces: List[Force] = [NewtonianGravity(), DragForce(), CoriolisForce(), EotvosForce(), CentrifugalForce()]

    def add_force(self, force: Force) -> None:
        self.forces.append(force)

    def remove_force(self, force: Force) -> None:
        for f in self.forces:
            if type(f) == type(force):
                self.forces.remove(f)
                return
        print("Non-existing force {}!".format(type(force).__name__))

    # noinspection PyPep8Naming
    def density(self, altitude: float) -> float:
        """Works up to 86km; above that, things start falling apart (literally, air molecules start falling apart)"""
        if altitude > 100000:
            return 0
        h = altitude
        rho_b = self.atmosphere.mass_density(h)
        T = self.atmosphere.base_temp(h)
        L = self.atmosphere.temp_lapse_rate(h)
        g_0 = self.std_gravity
        h_b = self.atmosphere.atmosphere_layer_start(h)
        M = self.atmosphere.molar_mass(h)
        if L == 0:
            return rho_b * exp((-g_0 * M * (h - h_b)) / (R * T))
        else:
            return rho_b * ((T / (T + L * (h-h_b))) ** (1 + ((g_0 * M) / (R * L))))

    def pressure(self, altitude: float) -> float:
        rho = self.density(altitude)
        temp = self.atmosphere.base_temp(altitude) + (altitude-self.atmosphere.atmosphere_layer_start(altitude)) \
             * self.atmosphere.temp_lapse_rate(altitude)
        return rho / self.atmosphere.molar_mass(altitude) * R * temp

    def get_forces_intensities(self, projectile) -> np.array:
        intensities = np.zeros([len(self.forces), 3], "float128")
        if DEBUG:
            print("Position: {}, {}, {}"
                  .format(projectile.position.lat, projectile.position.lon, projectile.position.alt))
        i = 0
        for force in self.forces:
            intensities[i] = np.array([force.get_x(projectile, self), force.get_y(projectile, self),
                                       force.get_z(projectile, self)])
            i += 1
        if DEBUG:
            print(intensities)
            print("\n")

        return intensities

    def create_projectile(self, mass: float, initial_position: Position, cross_section=lambda axis, pitch, yaw: 0.25,
                          drag_coef=lambda axis, pitch, yaw: 0.05, forces_writer=None) -> Projectile:
        return Projectile(self, mass, [0, 0, 0], initial_position, cross_section, drag_coef,
                          forces_writer=forces_writer)

    def plot_all_forces(self, forces_filename: str):
        i = 0
        for force in self.forces:
            simple_force_plot(ForcesCsvReader(forces_filename), i, type(force).__name__)
            i += 1
