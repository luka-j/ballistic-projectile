from __future__ import annotations

from math import cos, sin, pi, atan2, asin, sqrt, fabs
from typing import List

import numpy as np

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.core.Position import Position
from projectile.data.DataPoint import DataPoint
from projectile.util import sgn, RollingStatistic, haversine


class Projectile:
    def __init__(self, environment: Environment, mass: float, initial_velocities: List[float],
                 initial_position: Position, cross_section=lambda axis, pitch, yaw: 0.25,
                 drag_coef=lambda axis, pitch, yaw: 0.1, vy_corrective_change_threshold=0.1,
                 distance_rolling_window=40):
        if initial_position is None:
            initial_position = Position(44.869389, 20.640221, 0)
        self.initial_mass = mass
        self.velocities = np.array(initial_velocities, "float64")
        self.position = initial_position
        self.cross_section = cross_section
        self.drag_coef = drag_coef
        self.environment = environment
        self.vy_corrective_change_threshold = vy_corrective_change_threshold
        self.crossed_the_pole = False
        self.directions = np.zeros(3)
        self.time = 0
        self.lost_mass = 0
        self.distance_travelled = 0
        self.total_velocity = 0
        self.pitch = 0
        self.yaw = 0
        self.dt = 0
        self.thrust = None
        self.distance_stats = RollingStatistic(distance_rolling_window)

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
        self.thrust = thrust

    def advance(self, dt):
        self.dt = dt
        forces = self.environment.get_forces_intensity(self)
        acc = forces / self.mass()
        self.velocities += acc * dt
        self.total_velocity = np.sqrt(np.sum(self.velocities ** 2))
        self.directions = np.sign(self.velocities)
        movements = self.velocities * dt

        radius = self.environment.earth_radius + self.position.alt
        distance_m = np.sqrt(movements[X_INDEX] ** 2 + movements[Y_INDEX] ** 2)
        distance_rad = distance_m / radius

        angle = self.yaw - pi/2
        old_lat = self.position.lat
        old_lon = self.position.lon
        self.position.lat = asin(sin(self.position.lat) * cos(distance_rad) +
                                 cos(self.position.lat) * sin(distance_rad) * cos(angle))
        self.directions[Y_INDEX] = sgn(self.position.lat - old_lat)
        if cos(self.position.lat) != 0:
            self.position.lon = \
                divmod(self.position.lon - asin(sin(angle) * sin(distance_rad) / cos(self.position.lat)) + pi,
                       2 * pi)[1] - pi
        self.position.alt += self.velocities[Z_INDEX] * dt

        self.time += dt
        self.distance_travelled += distance_m
        # first update angles, then velocities: otherwise, low intensity forces (e.g. Coriolis) will be lost in rounding
        self.update_angles()
        self.update_velocities(old_lat, old_lon, radius, distance_m)

    def update_velocities(self, old_lat: np.float128, old_lon: np.float128, radius: float, distance_m: float) -> None:
        old_vy = self.velocities[Y_INDEX]
        self.velocities[Y_INDEX] = (radius * (self.position.lat - old_lat)) / self.dt
        change_ratio = fabs(self.velocities[Y_INDEX] / old_vy - 1)
        if change_ratio > self.vy_corrective_change_threshold:
            actual_distance = haversine(self.position, Position(old_lat, old_lon, 0), radius)
            if self.crossed_the_pole:
                print("Warning! V_y has too extreme oscillations: %f" % change_ratio)
            elif actual_distance < self.distance_stats.mean and self.distance_stats.is_outlier(actual_distance):
                # assume we've just crossed the pole
                print("Crossing the pole: change ratio is %f" % change_ratio)
                self.velocities[Y_INDEX] = -old_vy
                self.crossed_the_pole = True
                self.position.lon = divmod(self.position.lon + pi, 2 * pi)[1]
                self.velocities[X_INDEX] = -self.velocities[X_INDEX]
                return  # don't update X velocity!
            elif actual_distance < self.distance_stats.mean:
                print("Warning: Vy has extreme correction, but we're far from poles: %f" % change_ratio)
        if self.crossed_the_pole:
            self.crossed_the_pole = False
            self.velocities[Y_INDEX] = old_vy  # don't correct speed if we've just skipped the pole
            return

        self.distance_stats.update(distance_m)
        lon_radius = radius * cos(self.position.lat)
        if lon_radius == 0:
            # not much we can do on the poles, just use the last good number, it'll be close enough
            lon_radius = radius * cos(old_lat)
        if fabs(self.position.lon - old_lon) < pi:  # normal case
            self.velocities[X_INDEX] = (lon_radius * (self.position.lon - old_lon)) / self.dt
        else:  # crossing the antimeridian
            self.velocities[X_INDEX] = (lon_radius * (self.position.lon - old_lon +
                                                      2 * pi * sgn(old_lon - self.position.lon))) / self.dt

    def update_angles(self) -> None:
        self.pitch = atan2(self.velocities[Z_INDEX],
                           sqrt(self.velocities[X_INDEX] ** 2 + self.velocities[Y_INDEX] ** 2))
        self.yaw = atan2(self.velocities[Y_INDEX], self.velocities[X_INDEX])

    def mass(self) -> float:
        return self.initial_mass - self.lost_mass

    def has_hit_ground(self) -> bool:
        return self.position.alt <= self.environment.surface_altitude(self.position)

    def get_state(self) -> DataPoint:
        fuel = 0
        if self.thrust is not None:
            fuel = self.thrust.remaining_fuel
        return DataPoint(self.time, self.distance_travelled, self.position.lat, self.position.lon, self.position.alt,
                         self.velocities[X_INDEX], self.velocities[Y_INDEX], self.velocities[Z_INDEX],
                         self.pitch, self.yaw, fuel)
