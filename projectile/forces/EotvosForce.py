from math import cos

from projectile.core.Constants import X_INDEX
from projectile.forces.Force import Force


class EotvosForce(Force):
    """
    Vertical component of CoriolisForce. Acts upwards when going east, downwards when going west.
    """
    def __init__(self):
        super().__init__(lambda pr, env: 0,
                         lambda pr, env: 0,
                         lambda pr, env: 2 * pr.directions[X_INDEX] * env.earth_angular_velocity
                                           * pr.planar_velocity * cos(pr.position.lat))
