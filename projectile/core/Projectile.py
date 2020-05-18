from __future__ import annotations

from math import cos, sin, pi, atan2, asin, sqrt, fabs
from typing import List

import numpy as np

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.core.Position import Position
from projectile.data.DataPoints import ProjectileDataPoint, ForcesDataPoint
from projectile.util import sgn, RollingStatistic, haversine, fp_eq


class Projectile:
    """
    Projectile which flies through the environment. Most of the interesting stuff is here.
    """
    def __init__(self, environment: Environment, mass: float, initial_velocities: List[float],
                 initial_position: Position, cross_section=lambda axis, pitch, yaw: 0.25,
                 drag_coef=lambda axis, pitch, yaw: 0.1, vy_corrective_change_threshold=0.1,
                 distance_rolling_window=40, forces_writer: ForcesCsvWriter = None):
        if initial_position is None:
            initial_position = Position(44.869389, 20.640221, 0)
        self.initial_mass = mass
        self.velocities = np.array(initial_velocities, "float64")
        self.position = initial_position
        self.cross_section = cross_section
        self.drag_coef = drag_coef
        self.environment = environment
        self.vy_corrective_change_threshold = vy_corrective_change_threshold
        self.forces_writer = forces_writer
        self.crossed_the_pole = False
        self.directions = np.zeros(3)
        self.time = 0
        self.lost_mass = 0
        self.distance_travelled = 0
        self.total_velocity = 0
        self.planar_velocity = 0
        self.pitch = 0
        self.yaw = 0
        self.dt = 0
        self.thrust = None
        self.distance_stats = RollingStatistic(distance_rolling_window)

    def launch_at_angle(self, pitch: float, yaw: float, velocity: float) -> None:
        """
        Set initial velocities given total velocity and pitch and yaw.
        :param pitch:
        :param yaw:
        :param velocity: total velocity
        :return: nothing; projectile's state is modified
        """
        self.pitch = pitch
        self.yaw = yaw
        self.velocities[X_INDEX] = velocity * cos(yaw) * cos(pitch)
        self.velocities[Y_INDEX] = velocity * sin(yaw) * cos(pitch)
        self.velocities[Z_INDEX] = velocity * sin(pitch)

    def set_initial_velocities(self, vx: float, vy: float, vz: float) -> None:
        """
        Set initial velocities for each axis; pitch and yaw are calculated according to these values.
        :param vx: velocity in x direction (eastward)
        :param vy: velocity in y direction (northward)
        :param vz: velocity in z direction (upward)
        :return: nothing; projectile's state is modified
        """
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

    def advance(self, dt) -> None:
        """
        Advance the projectile for dt seconds. Heart of the simulation.
        :param dt: time which has passed.
        :return: nothing; projectile's state is modified.
        """
        self.dt = dt  # save this - forces may need this
        forces = self.environment.get_forces_intensities(self)  # calculate forces based on previous iteration's state
        if self.forces_writer is not None:  # if there's a ForcesWriter, we're writing these intensities to file (so
            self.forces_writer.write_data(ForcesDataPoint(self.time, self.mass(), forces))  # they can be plot later)
        acc = forces.sum(0) / self.mass()
        self.velocities += acc * dt
        # velocity in plane parallel to earth surface - 'distance travelled'
        self.planar_velocity = sqrt(self.velocities[X_INDEX] ** 2 + self.velocities[Y_INDEX] ** 2)
        # real, total velocity, taking z-axis into account as well
        self.total_velocity = sqrt(self.planar_velocity ** 2 + self.velocities[Z_INDEX] ** 2)
        self.directions = np.sign(self.velocities)  # this is useful for forces acting in opposite (or same) direction
        movements = self.velocities * dt

        # update pitch and yaw based on new velocities: we're using these angles (i.e. yaw) for calculating new position
        self.update_angles()
        radius = self.environment.earth_radius + self.position.alt
        distance_m = np.sqrt(movements[X_INDEX] ** 2 + movements[Y_INDEX] ** 2)
        distance_rad = distance_m / radius  # distance travelled in radians

        angle = self.yaw - pi/2  # we're using formula which expects true course angle, not mathematical
        old_lat = self.position.lat
        old_lon = self.position.lon
        # Formula source: http://www.edwilliams.org/avform.htm#LL
        self.position.lat = asin(sin(self.position.lat) * cos(distance_rad) +
                                 cos(self.position.lat) * sin(distance_rad) * cos(angle))
        self.directions[Y_INDEX] = sgn(self.position.lat - old_lat)
        if not fp_eq(cos(self.position.lat), 0):  # if we're on a pole, just don't do anything (this is _very_ rare)
            self.position.lon = \
                divmod(self.position.lon - asin(sin(angle) * sin(distance_rad) / cos(self.position.lat)) + pi,
                       2 * pi)[1] - pi
        self.position.alt += self.velocities[Z_INDEX] * dt  # we're calculating z-movement in the usual way

        self.time += dt
        self.distance_travelled += distance_m
        # now that we've moved, recalculate x/y/z speeds: we've changed a local tangent plane, so they've changed too
        self.update_velocities(old_lat, old_lon, radius, distance_m)
        # lastly, update angles so in the next iteration forces will use angles based on new (recalculated) speeds
        self.update_angles()

    def update_velocities(self, old_lat: np.float128, old_lon: np.float128, radius: float, distance_m: float) -> None:
        """
        Update velocities: take a look at the old position, current position, how much it has changed and calculate the
        speed based on that. Effectively moves the local tangent plane. z-speed is not modified as it's unaffected by
        moving of the tangent plane.
        :param old_lat: previous latitude
        :param old_lon: previous longitude
        :param radius: earth radius + altitude
        :param distance_m: distance travelled (could be calculated inside the function, but no need atm)
        :return: nothing; updates the projectile's state
        """
        old_vy = self.velocities[Y_INDEX]
        self.velocities[Y_INDEX] = (radius * (self.position.lat - old_lat)) / self.dt  # usual case for correcting Vy
        # our first and largest problem is detecting whether we've crossed the pole. I don't know a nice way for this,
        # so we use the ugly way: statistics and prayers.
        # ideally, change_radio should be 0 (meaning Vy won't be corrected)
        change_ratio = fabs(self.velocities[Y_INDEX] / old_vy - 1)
        if change_ratio > self.vy_corrective_change_threshold:  # oops, we've modified Vy too much
            actual_distance = haversine(self.position, Position(old_lat, old_lon, 0), radius)
            if self.crossed_the_pole:  # if we've crossed the pole recently, we definitely don't want to do it again
                print("Warning! V_y has too extreme oscillations: %f" % change_ratio)
            elif actual_distance < self.distance_stats.mean and self.distance_stats.is_outlier(actual_distance):
                # if we've travelled significantly less than usual (i.e. in y direction), assume we've crossed the pole
                # conceptually simple, practically not-really-definable, but surprisingly effective
                print("Crossing the pole: change ratio is %f" % change_ratio)
                # so now that we've crossed the pole, we want to reverse Vx and Vy and change longitude so we continue
                # flying 'straight'. We're basically throwing away this iteration and using the data from the previous.
                self.velocities[Y_INDEX] = -old_vy
                self.crossed_the_pole = True  # this will prevent crossing the pole again if we're still too close
                self.position.lon = divmod(self.position.lon + pi, 2 * pi)[1]
                self.velocities[X_INDEX] = -self.velocities[X_INDEX]
                return  # don't update X velocity!
            elif actual_distance < self.distance_stats.mean:
                # Vy changed a lot, but we're far away from the pole; can happen in e.g. polar circle even if we're not
                # flying over the pole itself.
                print("Warning: Vy has extreme correction, but we're far from poles: %f" % change_ratio)
        if self.crossed_the_pole:
            self.crossed_the_pole = False
            self.velocities[Y_INDEX] = old_vy  # don't correct speed if we've just skipped the pole
            return

        self.distance_stats.update(distance_m)  # we need to keep track of what's the 'usual' movement
        # from now on, we take care of updating Vx
        lon_radius = radius * cos(self.position.lat)
        if lon_radius == 0:
            # not much we can do if we're exactly at the pole, just use the last good number, it'll be close enough
            lon_radius = radius * cos(old_lat)
        if fabs(self.position.lon - old_lon) < pi:  # usual case for correcting Vx
            self.velocities[X_INDEX] = (lon_radius * (self.position.lon - old_lon)) / self.dt
        else:  # crossing the antimeridian: we haven't really moved for 2pi, so substract (or add) that
            self.velocities[X_INDEX] = (lon_radius * (self.position.lon - old_lon +
                                                      2 * pi * sgn(old_lon - self.position.lon))) / self.dt

    def update_angles(self) -> None:
        """
        Update pitch and yaw based on current velocities.
        :return: nothing; updates the projectile's state
        """
        self.pitch = atan2(self.velocities[Z_INDEX],
                           sqrt(self.velocities[X_INDEX] ** 2 + self.velocities[Y_INDEX] ** 2))
        self.yaw = atan2(self.velocities[Y_INDEX], self.velocities[X_INDEX])

    def mass(self) -> float:
        return self.initial_mass - self.lost_mass

    def has_hit_ground(self) -> bool:
        return self.position.alt <= self.environment.surface_altitude(self.position)

    def get_state(self) -> ProjectileDataPoint:
        """
        Get state in a convenient format for writing to file
        :return: DataPoint for current projectile state
        """
        fuel = 0
        if self.thrust is not None:
            fuel = self.thrust.remaining_fuel
        return ProjectileDataPoint(self.time, self.distance_travelled, self.position.lat, self.position.lon, self.position.alt,
                                   self.velocities[X_INDEX], self.velocities[Y_INDEX], self.velocities[Z_INDEX],
                                   self.pitch, self.yaw, fuel)
