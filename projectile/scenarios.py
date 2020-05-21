import math
import os
import shutil

from joblib import Parallel, delayed

from projectile.core.Constants import Z_INDEX
from projectile.core.Environment import Environment
from projectile.core.Launcher import Launcher
from projectile.core.Position import Position
from projectile.core.Projectile import Projectile
from projectile.forces.CentrifugalForce import CentrifugalForce
from projectile.forces.CoriolisForce import CoriolisForce
from projectile.forces.ThrustForce import follow_path, ThrustForce
from projectile.util import spherical_to_planar_coord, Stopwatch


if not os.path.exists("scenario_data"):
    os.mkdir("scenario_data")


def init_scenario(name: str) -> (str, str, str, Stopwatch):  # create files and initialize Stopwatch
    os.mkdir("scenario_data/{}/".format(name))
    csvdir = "scenario_data/{}/csv/".format(name)
    kmldir = "scenario_data/{}/kml/".format(name)
    frcdir = "scenario_data/{}/forces/".format(name)
    os.mkdir(csvdir)
    os.mkdir(kmldir)
    os.mkdir(frcdir)
    stopwatch = Stopwatch()
    return csvdir, kmldir, frcdir, stopwatch


def run(scenario: str, args=None) -> None:
    """
    Run a scenario. Invokes a method by name. All scenarios are defined in this function with local scope.
    :param scenario: scenario to be run
    :param args: arguments to be passed to the scenario
    :return: nothing; scenario is run and its output is probably in a file
    """

    def vary_latitude() -> None:
        """
        Launch long-distance flights to the east, varying the latitude, across the same meridian. Total 170 flights.
        :return: nothing
        """
        print("Running {}".format(scenario))

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

        def iteration(latitude: float):
            env = Environment(surface_altitude=lambda p: 80)
            thrust = ThrustForce(5000, fuel_flow, 150, 250000, 15, thrust_direction)
            launcher = Launcher(math.pi / 4, 0, "%s%d.csv" % (csvdir, latitude), "%s%d" % (kmldir, latitude),
                                "%s%d.csv" % (frcdir, latitude), environment=env, thrust=thrust)
            launcher.launch(10000, Position(math.radians(latitude), math.radians(45), 80))
            stopwatch.lap()

        core_number = -1
        if args is not None and len(args) > 0:
            core_number = int(args[0])
        Parallel(core_number)(delayed(iteration)(i) for i in range(-85, 85))

        stopwatch.stop()

    def vary_yaw() -> None:
        """
        Launch long-distance flights with pi/4 pitch with varying yaws. Total 71 flights.
        :return: nothing
        """
        print("Running {}".format(scenario))

        def fuel_flow(t: float):
            if t < 1:
                return 1000
            if t < 3:
                return 500
            return 100

        csvdir, kmldir, frcdir, stopwatch = init_scenario("ld_vary_yaw")
        stopwatch.start()

        def iteration(yaw: int):
            def thrust_direction(axis: int, force: float, pr: Projectile):
                if pr.time < 1.2:
                    return spherical_to_planar_coord(axis, force, math.pi / 4, math.radians(yaw))
                if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 4000) and pr.pitch > 0.2:
                    spherical_to_planar_coord(axis, force, pr.pitch - 0.15, pr.yaw)
                if pr.pitch < 0.15:
                    spherical_to_planar_coord(axis, force, pr.pitch + 0.17, pr.yaw)
                return follow_path(axis, force, pr)

            env = Environment(surface_altitude=lambda p: 80)
            thrust = ThrustForce(5000, fuel_flow, 150, 250000, 15, thrust_direction)
            launcher = Launcher(math.pi / 4, math.radians(yaw), "%s%d.csv" % (csvdir, yaw), "%s%d" % (kmldir, yaw),
                                "%s%d.csv" % (frcdir, yaw), environment=env, thrust=thrust)
            launcher.launch(10000, Position(math.radians(0), math.radians(15), 80))
            # compress("%s%d.csv" % (csvdir, yaw), "%s%d.bz2" % (csvdir, yaw), name_inside_zip="%d.csv" % yaw,
            #         keep_original=False)
            # compress("%s%d.csv" % (frcdir, yaw), "%s%d.bz2" % (frcdir, yaw), name_inside_zip="%d.csv" % yaw,
            #         keep_original=False)
            stopwatch.lap()

        core_number = -1
        if args is not None and len(args) > 0:
            core_number = int(args[0])
        Parallel(core_number)(delayed(iteration)(i) for i in range(0, 359, 5))

    def vary_pitch() -> None:
        """
        Launch long-distance flights to the east with varying pitches (8-82). Total 38 flights.
        :return: nothing
        """
        print("Running {}".format(scenario))

        def fuel_flow(t: float):
            if t < 1:
                return 1000
            if t < 3:
                return 500
            return 100

        csvdir, kmldir, frcdir, stopwatch = init_scenario("ld_vary_pitch")
        stopwatch.start()

        def iteration(pitch: float):
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
            stopwatch.lap()

        core_number = -1
        if args is not None and len(args) > 0:
            core_number = int(args[0])
        Parallel(core_number)(delayed(iteration)(i) for i in range(8, 82, 2))
        stopwatch.stop()

    def long_distance() -> None:
        print("Running {}".format(scenario))

        def thrust_direction(axis: int, force: float, pr: Projectile):
            if pr.time < 1:
                return spherical_to_planar_coord(axis, force, math.pi / 4, math.pi)
            if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 3500) and pr.pitch > 0.2:
                spherical_to_planar_coord(axis, force, pr.pitch - 0.2, pr.yaw)
            if pr.pitch < 0.15:
                spherical_to_planar_coord(axis, force, pr.pitch + 0.1, pr.yaw)
            return follow_path(axis, force, pr)
        if os.path.exists("scenario_data/long_distance/"):
            shutil.rmtree("scenario_data/long_distance/")
        csvdir, kmldir, frcdir, stopwatch = init_scenario("long_distance")
        stopwatch.start()

        env = Environment(surface_altitude=lambda p: 80)
        thrust = [ThrustForce(4000, lambda t: 120, 150, 200000, 12, thrust_direction),
                  ThrustForce(1800, lambda t: 150, 150, 200000, 13, thrust_direction),
                  ThrustForce(1200, lambda t: 200, 200, 300000, 15, thrust_direction),
                  ThrustForce(1200, lambda t: 200, 200, 300000, 15, thrust_direction)]
        launcher = Launcher(math.pi/4, math.pi, "%sdata.csv" % csvdir, "%sdata" % kmldir,
                            "%sdata.csv" % frcdir, environment=env, thrust=thrust)
        launcher.launch(10000, Position(math.radians(10), math.radians(-10), 80))
        stopwatch.stop()
        env.plot_all_forces("%sdata.csv" % frcdir)

    def test() -> None:
        """
        Test scenario. Default for fiddling around.
        :return: nothing
        """
        print("Running {}".format(scenario))

        def fuel_flow(t: float):
            if t < 1:
                return 600
            if t < 3:
                return 300
            return 100

        def thrust_direction(axis: int, force: float, pr: Projectile):
            if pr.time < 1.2:
                return spherical_to_planar_coord(axis, force, 0.9, 0)
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

    def pole_crossing() -> None:
        """
        Start really north. Cross the pole and carry on.
        :return: nothing
        """
        print("Running {}".format(scenario))

        def fuel_flow(t: float):
            if t < 1:
                return 600
            if t < 3:
                return 400
            return 100

        def thrust_direction(axis: int, force: float, pr: Projectile):
            if pr.time < 1.2:
                return spherical_to_planar_coord(axis, force, math.pi/4, math.pi/2)
            if (pr.position.alt > 100000 or pr.velocities[Z_INDEX] > 3500) and pr.pitch > 0.2:
                spherical_to_planar_coord(axis, force, pr.pitch - 0.12, pr.yaw)
            if pr.pitch < 0.15:
                spherical_to_planar_coord(axis, force, pr.pitch + 0.17, pr.yaw)
            return follow_path(axis, force, pr)

        if os.path.exists("scenario_data/pole_crossing/"):
            shutil.rmtree("scenario_data/pole_crossing/")
        csvdir, kmldir, frcdir, stopwatch = init_scenario("pole_crossing")
        stopwatch.start()

        env = Environment(surface_altitude=lambda p: 80)
        env.remove_force(CoriolisForce())
        env.remove_force(CentrifugalForce())
        thrust = ThrustForce(4000, fuel_flow, 150, 200000, 12, thrust_direction)
        launcher = Launcher(math.pi/4, math.pi/2, "%stest.csv" % csvdir, "%stest" % kmldir,
                            "%stest.csv" % frcdir, environment=env, thrust=thrust, dt=0.1)
        launcher.launch(8000, Position(math.radians(84), math.radians(-15), 80))
        stopwatch.stop()
        env.plot_all_forces("%stest.csv" % frcdir)

    #
    locals()[scenario]()  # call the appropriate method
