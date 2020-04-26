from __future__ import annotations
from projectile.forces.Force import Force
from math import cos, sin


class ThrustForce(Force):
    def dv(self, projectile: Projectile) -> float:
        if self.remaining_fuel <= 0:
            return 0
        if self.last_time == projectile.time:
            return self.last_result
        self.last_time = projectile.time
        burn_fuel = min(self.fuel_flow * projectile.dt, self.remaining_fuel)
        mass_before = projectile.mass()
        projectile.lost_mass += burn_fuel
        self.remaining_fuel -= burn_fuel
        velocity = projectile.total_velocity * mass_before/projectile.mass()
        dv = velocity - projectile.total_velocity
        self.last_result = dv
        return dv

    def __init__(self, total_fuel: float, fuel_flow: float):
        self.remaining_fuel = total_fuel
        self.fuel_flow = fuel_flow
        self.last_time = 0
        self.last_result = 0
        super().__init__(lambda pr, env: (self.dv(pr) * cos(pr.yaw) * cos(pr.pitch))/(pr.dt**2),
                         lambda pr, env: (self.dv(pr) * sin(pr.yaw) * cos(pr.pitch))/(pr.dt**2),
                         lambda pr, env: (self.dv(pr) * sin(pr.pitch))/(pr.dt**2))
