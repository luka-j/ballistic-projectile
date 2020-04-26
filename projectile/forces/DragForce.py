from __future__ import annotations

from projectile.Projectile import Projectile
from projectile.forces.Force import Force


# noinspection PyUnresolvedReferences
def intensity(projectile: Projectile, environment: Environment, velocity: float):
    return 0.5 * environment.density(projectile.position.alt) * velocity ** 2 * \
           projectile.cross_section(projectile.pitch, projectile.yaw) * \
           projectile.drag_coef(projectile.pitch, projectile.yaw)


class DragForce(Force):
    def __init__(self):
        super().__init__(lambda p, env: -p.directions[0] * intensity(p, env, p.velocities[0]),
                         lambda p, env: -p.directions[1] * intensity(p, env, p.velocities[1]),
                         lambda p, env: -p.directions[2] * intensity(p, env, p.velocities[2]))
