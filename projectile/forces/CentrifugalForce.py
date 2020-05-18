from __future__ import annotations

from math import cos, sin, fabs

from projectile.core.Projectile import Projectile
from projectile.forces.Force import Force
from projectile.util import sgn


# noinspection PyUnresolvedReferences
def intensity(projectile: Projectile, environment: Environment):
    return environment.earth_angular_velocity**2 * environment.earth_radius * cos(projectile.position.lat)


class CentrifugalForce(Force):
    """
    Centrifugal force acts towards the equator and upwards.
    """
    def __init__(self):
        super().__init__(lambda pr, env: 0,
                         lambda pr, env: intensity(pr, env) * (-sgn(pr.position.lat)) * cos(pr.position.lat),
                         lambda pr, env: intensity(pr, env) * fabs(sin(pr.position.lat)))
