from math import sin, cos

from projectile.core.Constants import Y_INDEX, X_INDEX, Z_INDEX
from projectile.forces.Force import Force


class CoriolisForce(Force):
    """
    Coriolis force acts to the right if we're in northern hemisphere, to the left otherwise. If Vx is positive
    (projectile is travelling eastward), it lifts the projectile up; otherwise, it pushes projectile down.
    Source: https://en.wikipedia.org/wiki/Coriolis_force#Rotating_sphere
    See: https://en.wikipedia.org/wiki/Coriolis_force#/media/File:Earth_coordinates.svg
    """
    def __init__(self):
        super().__init__(lambda pr, env: 2 * env.earth_angular_velocity * pr.mass()
                                           * (pr.velocities[Y_INDEX] * sin(pr.position.lat) -
                                              pr.velocities[Z_INDEX] * cos(pr.position.lat)),
                         lambda pr, env: 2 * env.earth_angular_velocity * pr.mass()
                                           * (-pr.velocities[X_INDEX] * sin(pr.position.lat)),
                         lambda pr, env: 2 * env.earth_angular_velocity * pr.mass()
                                           * (pr.velocities[X_INDEX] * cos(pr.position.lat)))
