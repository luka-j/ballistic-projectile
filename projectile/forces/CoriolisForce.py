from math import sin

from projectile.forces.Force import Force


class CoriolisForce(Force):
    def __init__(self):
        super().__init__(lambda pr, env: 2*env.earth_angular_velocity*pr.total_velocity*sin(pr.position.lat),
                         lambda pr, env: 0,
                         lambda pr, env: 0)
