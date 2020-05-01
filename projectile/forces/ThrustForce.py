from __future__ import annotations
from projectile.forces.Force import Force
from math import cos, sin
from typing import Callable
from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX


def follow_path(axis: int, force: float, pr: Projectile):
    if axis == X_INDEX:
        return force * cos(pr.yaw) * cos(pr.pitch)
    if axis == Y_INDEX:
        return force * sin(pr.yaw) * cos(pr.pitch)
    if axis == Z_INDEX:
        return force * sin(pr.pitch)


class ThrustForce(Force):
    def total_intensity(self, projectile: Projectile, env: Environment) -> float:
        if self.remaining_fuel <= 0:
            return 0
        if self.last_time == projectile.time:
            return self.last_result
        self.last_time = projectile.time
        burn_fuel = min(self.fuel_flow(projectile.time) * projectile.dt, self.remaining_fuel)
        g_0 = env.std_gravity
        F = g_0 * self.specific_impulse * burn_fuel
        self.last_result = F
        return F

    def __init__(self, specific_impulse_s: float, total_fuel: float, fuel_flow: Callable[[float], float],
                 direction_intensity: Callable[[int, float, Projectile], float] = follow_path):
        self.specific_impulse = specific_impulse_s
        self.direction_intensity = direction_intensity
        self.remaining_fuel = total_fuel
        self.fuel_flow = fuel_flow
        self.last_time = 0
        self.last_result = 0
        super().__init__(lambda pr, env: self.direction_intensity(X_INDEX, self.total_intensity(pr, env), pr),
                         lambda pr, env: self.direction_intensity(Y_INDEX, self.total_intensity(pr, env), pr),
                         lambda pr, env: self.direction_intensity(Z_INDEX, self.total_intensity(pr, env), pr))
