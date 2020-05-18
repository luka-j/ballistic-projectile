from __future__ import annotations

from typing import Callable

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.forces.Force import Force
from projectile.util import spherical_to_planar_coord


def follow_path(axis: int, force: float, pr: Projectile) -> float:
    return spherical_to_planar_coord(axis, force, pr.pitch, pr.yaw)


class ThrustForce(Force):
    """
    Defines thurst which moves the rocket. Main source of power. Consumes fuel to move.
    """
    def total_intensity(self, projectile: Projectile, env: Environment) -> float:
        if self.remaining_fuel <= 0:  # we don't have fuel, don't do anything
            return 0
        if self.last_time == projectile.time:  # if we've already calculated a value for this time point, return that
            return self.last_result
        # if not, consume fuel and calculate thrust
        self.last_time = projectile.time
        flow_rate = self.fuel_flow(projectile.time)
        burned_fuel = flow_rate * projectile.dt
        if burned_fuel > self.remaining_fuel:  # we're out of fuel, burn the remains
            burned_fuel = self.remaining_fuel
            flow_rate = burned_fuel / projectile.dt
        self.remaining_fuel -= burned_fuel
        projectile.lost_mass += burned_fuel

        # Source: https://www.grc.nasa.gov/WWW/K-12/rocket/rockth.html
        # thrust gained from exit velocity + thrust gained from pressure difference
        self.last_result = self.ejection_speed * flow_rate + \
                           (self.nozzle_pressure - env.pressure(projectile.position.alt)) * self.nozzle_exit_area
        return self.last_result

    def __init__(self, total_fuel: float, fuel_flow: Callable[[float], float], ejection_speed: float,
                 nozzle_pressure: float, nozzle_exit_area: float,
                 direction_intensity: Callable[[int, float, Projectile], float] = follow_path):
        self.direction_intensity = direction_intensity
        self.remaining_fuel = total_fuel
        self.fuel_flow = fuel_flow
        self.ejection_speed = ejection_speed
        self.nozzle_exit_area = nozzle_exit_area
        self.nozzle_pressure = nozzle_pressure
        self.last_time = -1
        self.last_result = 0
        super().__init__(lambda pr, env: self.direction_intensity(X_INDEX, self.total_intensity(pr, env), pr),
                         lambda pr, env: self.direction_intensity(Y_INDEX, self.total_intensity(pr, env), pr),
                         lambda pr, env: self.direction_intensity(Z_INDEX, self.total_intensity(pr, env), pr))
