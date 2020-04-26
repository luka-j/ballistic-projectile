import math
from typing import TextIO

from projectile.Environment import Environment
from projectile.Position import Position
from projectile.Projectile import Projectile
from projectile.forces.ThrustForce import ThrustForce

DT = 10**-2


def fly_projectile(projectile: Projectile, outfile: TextIO, dt: float):
    while True:
        projectile.advance(dt)
        projectile.write_position(outfile)
        if projectile.has_hit_ground():
            break


if __name__ == '__main__':
    env = Environment()
    projectile = env.create_projectile(5, Position(math.radians(44.869389), math.radians(20.640221), 0))
    projectile.launch_at_angle(math.pi / 4, math.pi/8, 10.0)
    projectile.add_thrust(ThrustForce(2, 2))
    output = open("/home/luka/Documents/mehanika-seminarski/test.out", "w")
    fly_projectile(projectile, output, DT)
    output.close()
    print("Finished!")
