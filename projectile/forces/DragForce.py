from __future__ import annotations

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.core.Projectile import Projectile
from projectile.forces.Force import Force


# noinspection PyUnresolvedReferences
def intensity(projectile: Projectile, environment: Environment, velocity: float, axis: int):
    return 0.5 * environment.density(projectile.position.alt) * velocity ** 2 * \
           projectile.cross_section(axis, projectile.pitch, projectile.yaw) * \
           projectile.drag_coef(axis, projectile.pitch, projectile.yaw)


class DragForce(Force):
    def __init__(self):
        super().__init__(lambda p, env: -p.directions[0] * intensity(p, env, p.velocities[X_INDEX], X_INDEX),
                         lambda p, env: -p.directions[1] * intensity(p, env, p.velocities[Y_INDEX], Y_INDEX),
                         lambda p, env: -p.directions[2] * intensity(p, env, p.velocities[Z_INDEX], Z_INDEX))
