import math

from projectile.Environment import Environment
from projectile.Position import Position
from projectile.Projectile import Projectile
from projectile.forces.ThrustForce import ThrustForce
from projectile.data.CsvWriter import CsvWriter
from projectile.data.KmlWriter import KmlWriter

DT = 10**-2


def fly_projectile(projectile: Projectile, outfile_name: str, dt: float):
    writer = CsvWriter(outfile_name)
    writer.write_header()
    kml = KmlWriter("/home/luka/Documents/mehanika-seminarski/test.kml")
    kml.write_header()
    while True:
        projectile.advance(dt)
        data = projectile.get_state()
        writer.write_data(data)
        kml.write(data)
        if projectile.has_hit_ground():
            break
    writer.close()
    kml.close()


if __name__ == '__main__':
    env = Environment()
    projectile = env.create_projectile(1, Position(math.radians(44.869389), math.radians(20.640221), 0))
    projectile.launch_at_angle(math.pi / 4, math.pi/8, 20.0)
    projectile.add_thrust(ThrustForce(5, lambda t: 10))
    fly_projectile(projectile, "/home/luka/Documents/mehanika-seminarski/test.csv", DT)
    print("Finished!")
