import math

from projectile.core.Environment import Environment
from projectile.core.Position import Position
from projectile.core.Projectile import Projectile
from projectile.data.CsvReader import CsvReader
from projectile.forces.ThrustForce import ThrustForce, follow_path
from projectile.data.CsvWriter import CsvWriter
from projectile.data.KmlWriter import KmlWriter
from projectile.data.ZipIO import compress
from projectile.util import spherical_to_planar_coord
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


LAUNCH_PITCH = math.pi / 4
LAUNCH_YAW = math.pi / 2


def fuel_flow(t: float):
    if t < 0.5:
        return 800
    if t < 2:
        return 600
    return 50


def thrust_direction(axis: int, force: float, pr: Projectile):
    if pr.time > 1:
        return follow_path(axis, force, pr)
    else:
        return spherical_to_planar_coord(axis, force, LAUNCH_PITCH, LAUNCH_YAW)


if __name__ == '__main__':
    env = Environment(surface_altitude=lambda p: 77)
    projectile = env.create_projectile(8000, Position(math.radians(80), math.radians(24), 77),
                                       lambda axis, pitch, yaw: 20)
    projectile.launch_at_angle(LAUNCH_PITCH, LAUNCH_YAW, 0)
    projectile.add_thrust(ThrustForce(2500, fuel_flow, 80, 200000, 20, thrust_direction))
    fly_projectile(projectile, "/home/luka/Documents/mehanika-seminarski/test.csv", DT)

#    if DEBUG:
    print("Total: ")
    print(env.total_forces_impact)
    convert_to_kmz("/home/luka/Documents/mehanika-seminarski/test.csv",
                   "/home/luka/Documents/mehanika-seminarski/test")
    print("Finished!")
