from __future__ import annotations

from typing import Callable

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.core.Projectile import Projectile


# noinspection PyUnresolvedReferences
class Force:
    """
    Base class for all forces. Subclass this to introduce new forces. Three lambdas need to be provided for this to
    work: first one will calculate intensity in x direction (eastward), second one in y direction (northward) and the
    last one in z direction (upward).
    """

    def __init__(self, x: Callable[[Projectile, Environment], float],
                 y: Callable[[Projectile, Environment], float],
                 z: Callable[[Projectile, Environment], float]):
        self.intensity = [None, None, None]
        self.intensity[X_INDEX] = x
        self.intensity[Y_INDEX] = y
        self.intensity[Z_INDEX] = z

    def get_x(self, projectile: Projectile, env: Environment) -> float:
        return self.intensity[X_INDEX](projectile, env)

    def get_y(self, projectile: Projectile, env: Environment) -> float:
        return self.intensity[Y_INDEX](projectile, env)

    def get_z(self, projectile: Projectile, env: Environment) -> float:
        return self.intensity[Z_INDEX](projectile, env)

    def get(self, axis) -> Callable[[Projectile, Environment], float]:
        return self.intensity[axis]
