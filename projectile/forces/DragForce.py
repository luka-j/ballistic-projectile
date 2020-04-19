from __future__ import annotations

from projectile.Projectile import Projectile
from projectile.forces.Force import Force


# noinspection PyUnresolvedReferences
def intensity(projectile: Projectile, environment: Environment):
    return 0.5 * environment.density(projectile.position.z) * projectile.velocity()**2 * \
           projectile.cross_section() * projectile.drag_coef()


class DragForce(Force):
    def __init__(self):
        self.intensity = [0, 0, 0]
        super().__init__(lambda p, env: -p.directions[0] * intensity(p, env),
                         lambda p, env: -p.directions[1] * intensity(p, env),
                         lambda p, env: -p.directions[2] * intensity(p, env))
