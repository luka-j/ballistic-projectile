from __future__ import annotations

from math import cos, sin

from projectile.core.Projectile import Projectile
from projectile.forces.Force import Force


# noinspection PyUnresolvedReferences
def intensity(projectile: Projectile, environment: Environment):
    return projectile.mass() * environment.earth_angular_velocity**2 \
           * environment.earth_radius * cos(projectile.position.lat)


class CentrifugalForce(Force):
    """
    Centrifugal force acts towards the equator and upwards.
    """
    def __init__(self):
        super().__init__(lambda pr, env: 0,
                         lambda pr, env: intensity(pr, env) * (-sin(pr.position.lat)),
                         lambda pr, env: intensity(pr, env) * cos(pr.position.lat))
