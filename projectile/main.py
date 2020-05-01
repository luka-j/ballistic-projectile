import math

from projectile.Environment import Environment
from projectile.Position import Position
from projectile.Projectile import Projectile
from projectile.data.CsvReader import CsvReader
from projectile.forces.ThrustForce import ThrustForce
from projectile.data.CsvWriter import CsvWriter
from projectile.data.KmlWriter import KmlWriter

DT = 10**-2


def fly_projectile(projectile: Projectile, outfile_name: str, dt: float):
    writer = CsvWriter(outfile_name)
    writer.write_header()
    while True:
        projectile.advance(dt)
        data = projectile.get_state()
        writer.write_data(data)
        if projectile.has_hit_ground():
            break
    writer.close()


def convert_to_kml(csv_name: str, kml_name: str):
    kml = KmlWriter(kml_name)
    csv = CsvReader(csv_name)
    kml.convert(csv, sample_rate=10)
    csv.close()


def fuel_flow(t: float):
    if t < 0.5:
        return 6000
    if t < 2:
        return 500
    return 50


if __name__ == '__main__':
    env = Environment(surface_altitude=lambda p: 77)
    projectile = env.create_projectile(50000, Position(math.radians(44.869389), math.radians(20.640221), 77),
                                       lambda axis, pitch, yaw: 20)
    projectile.launch_at_angle(2 * math.pi / 4, math.pi/2, 0)
    projectile.add_thrust(ThrustForce(6000, fuel_flow, 100, 300000, 20))
    fly_projectile(projectile, "/home/luka/Documents/mehanika-seminarski/test.csv", DT)
    convert_to_kml("/home/luka/Documents/mehanika-seminarski/test.csv",
                   "/home/luka/Documents/mehanika-seminarski/test.kml")
    print("Finished!")
