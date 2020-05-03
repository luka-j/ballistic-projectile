from typing import List

from projectile.Position import Position
from projectile.forces.CentrifugalForce import CentrifugalForce
from projectile.forces.CoriolisForce import CoriolisForce
from projectile.forces.DragForce import DragForce
from projectile.forces.EotvosForce import EotvosForce
from projectile.forces.Force import Force
from projectile.forces.NewtonianGravity import NewtonianGravity
from projectile.Projectile import Projectile
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX, DEBUG, R
from math import exp
import numpy as np


def std_temp_lapse_rate(h: float):
    if h < 11000: return -0.0065
    if h < 20000: return 0
    if h < 32000: return 0.001
    if h < 47000: return 0.0028
    if h < 51000: return 0
    if h < 71000: return -0.0028
    return -0.002


def std_mass_density(h: float):
    if h < 11000: return 1.2250
    if h < 20000: return 0.36391
    if h < 32000: return 0.08803
    if h < 47000: return 0.01322
    if h < 51000: return 0.00143
    if h < 71000: return 0.00086
    return 0.000064


def std_temp(h: float):
    if h < 11000: return 288.15
    if h < 20000: return 216.65
    if h < 32000: return 216.65
    if h < 47000: return 228.65
    if h < 51000: return 270.65
    if h < 71000: return 270.65
    return 214.65


def std_atmosphere_layer_start(h: float):
    if h < 11000: return 0
    if h < 20000: return 11000
    if h < 32000: return 20000
    if h < 47000: return 32000
    if h < 51000: return 47000
    if h < 71000: return 51000
    return 71000


def std_molar_mass(h: float):
    return 0.0289644  # this is a lie above 100km


class Environment:

    def __init__(self, earth_radius=6378137, earth_angular_velocity=7.2921159e-5, surface_altitude=lambda pos: 0,
                 std_gravity_acc=9.80665, std_temp=std_temp, temp_lapse_rate=std_temp_lapse_rate,
                 mass_density=std_mass_density, atmosphere_layers=std_atmosphere_layer_start, molar_mass=std_molar_mass):
        self.earth_radius = earth_radius
        self.earth_angular_velocity = earth_angular_velocity
        self.surface_altitude = surface_altitude
        self.std_gravity = std_gravity_acc
        self.std_temp = std_temp
        self.temp_lapse_rate = temp_lapse_rate
        self.mass_density = mass_density
        self.atmosphere_layer_start = atmosphere_layers
        self.molar_mass = molar_mass
        self.forces: List[Force] = [NewtonianGravity(), DragForce(), CoriolisForce(), EotvosForce(), CentrifugalForce()]
        self.total_forces_impact = np.zeros((len(self.forces), 3))
        # it'd be prettier if total_forces_impact was dict, but that kills performance

    def add_force(self, force: Force) -> None:
        self.forces.append(force)
        self.total_forces_impact = np.append(self.total_forces_impact, [[0, 0, 0]], 0)

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
        rho_b = self.mass_density(h)
        T = self.std_temp(h)
        L = self.temp_lapse_rate(h)
        g_0 = self.std_gravity
        h_b = self.atmosphere_layer_start(h)
        M = self.molar_mass(h)
        if L == 0:
            return rho_b * exp((-g_0 * M * (h - h_b)) / (R * T))
        else:
            return rho_b * ((T / (T + L * (h-h_b))) ** (1 + ((g_0 * M) / (R * L))))

    def pressure(self, altitude: float) -> float:
        rho = self.density(altitude)
        temp = self.std_temp(altitude) + (altitude-self.atmosphere_layer_start(altitude))*self.temp_lapse_rate(altitude)
        return rho / self.molar_mass(altitude) * R * temp

    def get_forces_intensity(self, projectile) -> np.array:
        intensities = np.zeros(3, "float128")
        if DEBUG:
            print("Position: {}, {}, {}"
                  .format(projectile.position.lat, projectile.position.lon, projectile.position.alt))
        i = 0
        for force in self.forces:
            xyz = np.array([force.get_x(projectile, self), force.get_y(projectile, self), force.get_z(projectile, self)])
            intensities += xyz
            self.total_forces_impact[i] += xyz
            i += 1
            if DEBUG:
                print("{}: {}, {}, {}".format(type(force).__name__, xyz[0], xyz[1], xyz[2]))
        if DEBUG:
            print("\n")
        return intensities

    def create_projectile(self, mass: float, initial_position: Position, cross_section=lambda axis, pitch, yaw: 0.25,
                          drag_coef=lambda axis, pitch, yaw: 0.05) -> Projectile:
        return Projectile(self, mass, [0, 0, 0], initial_position, cross_section, drag_coef)
