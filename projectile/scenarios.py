import math
import os
import shutil

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


def init_scenario(name: str) -> (str, str, str, Stopwatch):
    os.mkdir("scenario_data/{}/".format(name))
    csvdir = "scenario_data/{}/csv/".format(name)
    kmldir = "scenario_data/{}/kml/".format(name)
    frcdir = "scenario_data/{}/forces/".format(name)
    os.mkdir(csvdir)
    os.mkdir(kmldir)
    os.mkdir(frcdir)
    stopwatch = Stopwatch()
    return csvdir, kmldir, frcdir, stopwatch


def run(scenario: str) -> None:

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

        csvdir, kmldir, frcdir, stopwatch = init_scenario("ld_eastward_latitude")
        stopwatch.start()

        for i in range(-85, 85):
            env = Environment(surface_altitude=lambda p: 80)
            thrust = ThrustForce(5000, fuel_flow, 150, 250000, 15, thrust_direction)
            launcher = Launcher(math.pi / 4, 0, "%s%d.csv" % (csvdir, i), "%s%d" % (kmldir, i),
                                "%s%d.csv" % (frcdir, i), environment=env, thrust=thrust)
            launcher.launch(10000, Position(math.radians(i), math.radians(45), 80))
            compress("%s%d.csv" % (csvdir, i), "%s%d.bz2" % (csvdir, i), name_inside_zip="%d.csv" % i,
                     keep_original=False)
            compress("%s%d.csv" % (frcdir, i), "%s%d.bz2" % (frcdir, i), name_inside_zip="%d.csv" % i,
                     keep_original=False)
            stopwatch.lap()
        stopwatch.stop()

    def vary_yaw():
        print("Running vary_yaw")

        def fuel_flow(t: float):
            if t < 1:
                return 1000
            if t < 3:
                return 500
            return 100

        csvdir, kmldir, frcdir, stopwatch = init_scenario("ld_vary_yaw")
        stopwatch.start()

        for yaw in range(0, 359, 5):
            def thrust_direction(axis: int, force: float, pr: Projectile):
                if pr.time < 1.2:
                    return spherical_to_planar_coord(axis, force, math.pi / 4, yaw)
                if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 4000) and pr.pitch > 0.2:
                    spherical_to_planar_coord(axis, force, pr.pitch - 0.15, pr.yaw)
                if pr.pitch < 0.15:
                    spherical_to_planar_coord(axis, force, pr.pitch + 0.17, pr.yaw)
                return follow_path(axis, force, pr)

            env = Environment(surface_altitude=lambda p: 80)
            thrust = ThrustForce(5000, fuel_flow, 150, 250000, 15, thrust_direction)
            launcher = Launcher(math.pi / 4, yaw, "%s%d.csv" % (csvdir, yaw), "%s%d" % (kmldir, yaw),
                                "%s%d.csv" % (frcdir, yaw), environment=env, thrust=thrust)
            launcher.launch(10000, Position(math.radians(45), math.radians(45), 80))
            compress("%s%d.csv" % (csvdir, yaw), "%s%d.bz2" % (csvdir, yaw), name_inside_zip="%d.csv" % yaw,
                     keep_original=False)
            compress("%s%d.csv" % (frcdir, yaw), "%s%d.bz2" % (frcdir, yaw), name_inside_zip="%d.csv" % yaw,
                     keep_original=False)
            stopwatch.lap()

    def vary_pitch():
        print("Running vary_pitch")

        def fuel_flow(t: float):
            if t < 1:
                return 1000
            if t < 3:
                return 500
            return 100

        csvdir, kmldir, frcdir, stopwatch = init_scenario("ld_vary_pitch")
        stopwatch.start()

        for pitch in range(8, 80, 2):
            def thrust_direction(axis: int, force: float, pr: Projectile):
                if pr.time < 1.2:
                    return spherical_to_planar_coord(axis, force, math.radians(pitch), 0)
                if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 4000) and pr.pitch > 0.2:
                    spherical_to_planar_coord(axis, force, pr.pitch - 0.15, pr.yaw)
                if pr.pitch < 0.1:
                    spherical_to_planar_coord(axis, force, pr.pitch + 0.12, pr.yaw)
                return follow_path(axis, force, pr)

            env = Environment(surface_altitude=lambda p: 80)
            thrust = ThrustForce(5000, fuel_flow, 150, 250000, 15, thrust_direction)
            launcher = Launcher(math.radians(pitch), 0, "%s%d.csv" % (csvdir, pitch), "%s%d" % (kmldir, pitch),
                                "%s%d.csv" % (frcdir, pitch), environment=env, thrust=thrust)
            launcher.launch(10000, Position(math.radians(45), math.radians(45), 80))
            compress("%s%d.csv" % (csvdir, pitch), "%s%d.bz2" % (csvdir, pitch), name_inside_zip="%d.csv" % pitch,
                     keep_original=False)
            compress("%s%d.csv" % (frcdir, pitch), "%s%d.bz2" % (frcdir, pitch), name_inside_zip="%d.csv" % pitch,
                     keep_original=False)
            stopwatch.lap()

    def test():
        print("Running test")
        def fuel_flow(t: float):
            if t < 1:
                return 600
            if t < 3:
                return 300
            return 100

        def thrust_direction(axis: int, force: float, pr: Projectile):
            if pr.time < 1.2:
                return spherical_to_planar_coord(axis, force, math.pi / 4, 0)
            if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 3500) and pr.pitch > 0.2:
                spherical_to_planar_coord(axis, force, pr.pitch - 0.12, pr.yaw)
            if pr.pitch < 0.15:
                spherical_to_planar_coord(axis, force, pr.pitch + 0.17, pr.yaw)
            return follow_path(axis, force, pr)

        if os.path.exists("scenario_data/test/"):
            shutil.rmtree("scenario_data/test/")
        csvdir, kmldir, frcdir, stopwatch = init_scenario("test")
        stopwatch.start()

        env = Environment(surface_altitude=lambda p: 80)
        thrust = ThrustForce(3500, fuel_flow, 150, 200000, 12, thrust_direction)
        launcher = Launcher(0.9, 0, "%stest.csv" % csvdir, "%stest" % kmldir,
                            "%stest.csv" % frcdir, environment=env, thrust=thrust)
        launcher.launch(8000, Position(math.radians(60), math.radians(45), 80))
        stopwatch.stop()
        env.plot_all_forces("%stest.csv" % frcdir)

    #
    locals()[scenario]()
