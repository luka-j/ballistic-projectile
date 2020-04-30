from __future__ import annotations

from typing import List, TextIO
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.Position import Position
import numpy as np
from math import cos, sin, pi, atan2, asin, sqrt

from projectile.io.DataPoint import DataPoint
from projectile.util import sgn


class Projectile:
    def __init__(self, environment: Environment, mass: float, initial_velocities: List[float],
                 initial_position: Position, cross_section=lambda axis, pitch, yaw: 0.25,
                 drag_coef=lambda axis, pitch, yaw: 0.1):
        if initial_position is None:
            initial_position = Position(44.869389, 20.640221, 0)
        self.initial_mass = mass
        self.velocities = np.array(initial_velocities, "float64")
        self.position = initial_position
        self.cross_section = cross_section
        self.drag_coef = drag_coef
        self.environment = environment
        self.directions = np.zeros(3)
        self.time = 0
        self.lost_mass = 0
        self.distance_travelled = 0
        self.total_velocity = 0
        self.pitch = 0
        self.yaw = 0
        self.dt = 0

    def launch_at_angle(self, pitch: float, yaw: float, velocity: float) -> None:
        self.pitch = pitch
        self.yaw = yaw
        self.velocities[X_INDEX] = velocity * cos(yaw) * cos(pitch)
        self.velocities[Y_INDEX] = velocity * sin(yaw) * cos(pitch)
        self.velocities[Z_INDEX] = velocity * sin(pitch)

    def set_initial_velocities(self, vx: float, vy: float, vz: float) -> None:
        self.velocities[X_INDEX] = vx
        self.velocities[Y_INDEX] = vy
        self.velocities[Z_INDEX] = vz
        self.pitch = atan2(vz, sqrt(vx ** 2 + vy ** 2))
        self.yaw = atan2(vy, vx)

    def add_thrust(self, thrust: ThrustForce) -> None:
        """
        Add thrust force and fuel to the projectile.
        :param thrust: thrust force which will be added to the environment and fuel mass which will be
        added to the projectile
        """
        self.initial_mass += thrust.remaining_fuel
        self.environment.add_force(thrust)

    def advance(self, dt):
        self.dt = dt
        forces = self.environment.get_forces_intensity(self)
        acc = np.divide(forces, self.mass())
        self.velocities += acc * dt
        self.total_velocity = np.sqrt(np.sum(self.velocities ** 2))
        self.directions = np.sign(self.velocities)
        movements = self.velocities * dt

        radius = self.environment.earth_radius + self.position.alt
        distance_m = np.sqrt(movements[X_INDEX] ** 2 + movements[Y_INDEX] ** 2)
        distance_rad = distance_m / radius

        old_lat = self.position.lat
        old_lon = self.position.lon
        self.position.lat = asin(sin(self.position.lat) * cos(distance_rad) +
                                 cos(self.position.lat) * sin(distance_rad) * cos(self.yaw))
        self.directions[Y_INDEX] = sgn(self.position.lat - old_lat)
        if cos(self.position.lat) != 0:
            self.position.lon = \
                divmod(self.position.lon - asin(sin(self.yaw) * sin(distance_rad) / cos(self.position.lat)) + pi,
                       2 * pi)[1] - pi
        self.position.alt += self.velocities[Z_INDEX] * dt

        self.velocities[Y_INDEX] = (radius * (self.position.lat - old_lat))/dt
        lon_radius = radius * cos(self.position.lat)
        if lon_radius == 0:
            # not much we can do on the poles, just use the last good number, it'll be close enough
            lon_radius = radius * cos(old_lat)
        self.velocities[X_INDEX] = (lon_radius * (self.position.lon - old_lon))/dt
        self.pitch = atan2(self.velocities[Z_INDEX],
                           sqrt(self.velocities[X_INDEX] ** 2 + self.velocities[Y_INDEX] ** 2))
        self.yaw = atan2(self.velocities[Y_INDEX], self.velocities[X_INDEX])

        self.time += dt
        self.distance_travelled += distance_m

    def mass(self) -> float:
        return self.initial_mass - self.lost_mass

    def has_hit_ground(self) -> bool:
        return self.position.alt <= self.environment.surface_altitude(self.position)

    def get_state(self) -> DataPoint:
        return DataPoint(self.time, self.distance_travelled, self.position.lat, self.position.lon, self.position.alt,
                         self.velocities[X_INDEX], self.velocities[Y_INDEX], self.velocities[Z_INDEX],
                         self.pitch, self.yaw)
