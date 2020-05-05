from __future__ import annotations

from typing import Callable

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.forces.Force import Force
from projectile.util import spherical_to_planar_coord


def follow_path(axis: int, force: float, pr: Projectile):
    return spherical_to_planar_coord(axis, force, pr.pitch, pr.yaw)


class ThrustForce(Force):
    def total_intensity(self, projectile: Projectile, env: Environment) -> float:
        if self.remaining_fuel <= 0:
            return 0
        if self.last_time == projectile.time:
            return self.last_result
        self.last_time = projectile.time
        flow_rate = self.fuel_flow(projectile.time)
        burned_fuel = flow_rate * projectile.dt
        if burned_fuel > self.remaining_fuel:  # we're out of fuel, burn the remains
            burned_fuel = self.remaining_fuel
            flow_rate = burned_fuel / projectile.dt
        self.remaining_fuel -= burned_fuel

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
