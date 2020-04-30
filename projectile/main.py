import math
from typing import TextIO

from projectile.Environment import Environment
from projectile.Position import Position
from projectile.Projectile import Projectile
from projectile.forces.ThrustForce import ThrustForce
from projectile.io.CsvWriter import CsvWriter

DT = 10**-2


def fly_projectile(projectile: Projectile, outfile_name: str, dt: float):
    writer = CsvWriter(outfile_name)
    writer.write_header()
    while True:
        projectile.advance(dt)
        writer.write_data(projectile.get_state())
        if projectile.has_hit_ground():
            break
    writer.close()


if __name__ == '__main__':
    env = Environment()
    projectile = env.create_projectile(5, Position(math.radians(44.869389), math.radians(20.640221), 0))
    projectile.launch_at_angle(math.pi / 4, math.pi/8, 10.0)
    projectile.add_thrust(ThrustForce(5, lambda t: 10))
    fly_projectile(projectile, "/home/luka/Documents/mehanika-seminarski/test.csv", DT)
    print("Finished!")
