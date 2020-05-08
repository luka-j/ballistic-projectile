import math
import os

from projectile.core.Constants import Z_INDEX
from projectile.core.Environment import Environment
from projectile.core.Launcher import Launcher
from projectile.core.Position import Position
from projectile.core.Projectile import Projectile
from projectile.data.ZipIO import compress
from projectile.forces.ThrustForce import follow_path, ThrustForce
from projectile.util import spherical_to_planar_coord, Stopwatch


if not os.path.exists("scenario_data"):
    os.mkdir("scenario_data")


def run(scenario: str):

    def long_distance_eastward_across_meridian():
        print("Running long_distance_eastward_across_meridian")

        def fuel_flow(t: float):
            if t < 1:
                return 1000
            if t < 3:
                return 500
            return 100

        def thrust_direction(axis: int, force: float, pr: Projectile):
            if pr.time < 1.2:
                return spherical_to_planar_coord(axis, force, math.pi / 4, 0)
            if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 4000) and pr.pitch > 0.2:
                spherical_to_planar_coord(axis, force, pr.pitch - 0.15, pr.yaw)
            if pr.pitch < 0.15:
                spherical_to_planar_coord(axis, force, pr.pitch + 0.17, pr.yaw)
            return follow_path(axis, force, pr)

        os.mkdir("scenario_data/ld_eastward_latitude/")
        csvdir = "scenario_data/ld_eastward_latitude/csv/"
        kmldir = "scenario_data/ld_eastward_latitude/kml/"
        frcdir = "scenario_data/ld_eastward_latitude/forces/"
        os.mkdir(csvdir)
        os.mkdir(kmldir)
        os.mkdir(frcdir)

        stopwatch = Stopwatch()
        stopwatch.start()

        for i in range(-85, 85):
            env = Environment(surface_altitude=lambda p: 80)
            thrust = ThrustForce(5000, fuel_flow, 150, 250000, 15, thrust_direction)
            launcher = Launcher(math.pi / 4, 0, "%s/%d.csv" % (csvdir, i), "%s/%d" % (kmldir, i),
                                "%s/%d.csv" % (frcdir, i),
                                environment=env, thrust=thrust)
            launcher.launch(10000, Position(math.radians(i), math.radians(45), 80))
            compress("%s/%d.csv" % (csvdir, i), "%s/%d.bz2" % (csvdir, i), name_inside_zip="%d.csv" % i,
                     keep_original=False)
            compress("%s/%d.csv" % (csvdir, i), "%s/%d.bz2" % (csvdir, i), name_inside_zip="%d.csv" % i,
                     keep_original=False)
            stopwatch.lap()
        stopwatch.stop()

    #
    locals()[scenario]()
