import math

from projectile.Environment import Environment
from projectile.Position import Position
from projectile.Projectile import Projectile
from projectile.data.CsvReader import CsvReader
from projectile.forces.ThrustForce import ThrustForce
from projectile.data.CsvWriter import CsvWriter
from projectile.data.KmlWriter import KmlWriter
from projectile.Constants import DEBUG
from projectile.data.ZipIO import compress, uncompress
import zipfile

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


def convert_to_kmz(csv_name: str, kml_name: str):
    kml = KmlWriter(kml_name + ".kml")
    csv = CsvReader(csv_name)
    kml.convert(csv, sample_rate=10)
    compress(kml_name + ".kml", kml_name + ".kmz", zipfile.ZIP_DEFLATED, "doc.kml")


def fuel_flow(t: float):
    if t < 0.5:
        return 1200
    if t < 2:
        return 500
    return 50


if __name__ == '__main__':
    env = Environment(surface_altitude=lambda p: 77)
    projectile = env.create_projectile(10000, Position(math.radians(82), math.radians(172), 77),
                                       lambda axis, pitch, yaw: 20)
    projectile.launch_at_angle(math.pi / 3, math.pi/2, 0)
    projectile.add_thrust(ThrustForce(2800, fuel_flow, 70, 200000, 20))
    fly_projectile(projectile, "/home/luka/Documents/mehanika-seminarski/test.csv", DT)

#    if DEBUG:
    print("Total: ")
    print(env.total_forces_impact)
    convert_to_kmz("/home/luka/Documents/mehanika-seminarski/test.csv",
                   "/home/luka/Documents/mehanika-seminarski/test")
    print("Finished!")
