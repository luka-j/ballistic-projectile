from math import sin, cos, pi, fabs

from projectile.forces.Force import Force
from projectile.util import sgn


class CoriolisForce(Force):
    """
    Coriolis force acts to the right if we're in northern hemisphere, to the left otherwise. For vertical component,
    see EotvosForce.
    """
    def __init__(self):
        super().__init__(lambda pr, env: 2 * env.earth_angular_velocity * pr.planar_velocity
                                           * fabs(sin(pr.position.lat)) * cos(pr.yaw - sgn(pr.position.lat)*pi/2),
                         lambda pr, env: 2 * env.earth_angular_velocity * pr.planar_velocity
                                           * fabs(sin(pr.position.lat)) * sin(pr.yaw - sgn(pr.position.lat)*pi/2),
                         lambda pr, env: 0)
