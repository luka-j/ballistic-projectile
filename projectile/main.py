import math
from typing import TextIO

from projectile.Environment import Environment
from projectile.Position import Position
from projectile.Projectile import Projectile


def launch_projectile(projectile: Projectile, pitch: float, yaw: float, velocity: float,
                      outfile: TextIO, dt: float):
    projectile.launch_at_angle(pitch, yaw, velocity)
    while True:
        projectile.advance(dt)
        projectile.write_position(outfile)
        if projectile.has_hit_ground():
            break


if __name__ == '__main__':
    env = Environment()
    projectile = env.create_projectile(1, Position(44.869389, 20.640221, 0))
    output = open("/home/luka/Documents/mehanika-seminarski/test.out", "w")
    launch_projectile(projectile, math.pi / 4, math.pi/8, 10.0, output, 10**-2)
    output.close()
    print("Finished!")
