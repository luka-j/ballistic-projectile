import os
from typing import Union, List

from projectile.core.Environment import Environment
from projectile.core.Position import Position
from projectile.core.Projectile import Projectile
from projectile.data.CsvWriters import ProjectileCsvWriter, ForcesCsvWriter
from projectile.data.KmlWriter import convert_csv_to_kmz
from projectile.forces.ThrustForce import follow_path, ThrustForce
from projectile.util import spherical_to_planar_coord


class Launcher:
    """
    Utility class for launching projectiles. Takes care of setting up environment, projectiles and file I/O with
    specified values and/or sensible defaults and flying the projectile (main loop).
    """

    def default_thrust_direction(self, axis: int, force: float, pr: Projectile) -> float:
        """
        Sensible default for thrust direction. First two seconds it's flying in the same direction as it was launched.
        After then, if pitch is < 0.15, it attempts to correct it and flies upwards +0.17rad (relative to current).
        Otherwise, keeps the same direction.
        :param axis: axis for which thrust direction is caluclated
        :param force: total force intensity
        :param pr: projectile
        :return: thrust direction for the specified axis
        """
        if pr.time < 2:
            return spherical_to_planar_coord(axis, force, self.pitch, self.yaw)
        if pr.pitch < 0.15:
            spherical_to_planar_coord(axis, force, self.pitch + 0.17, self.yaw)
        return follow_path(axis, force, pr)

    def __init__(self, pitch, yaw, csv_filename, kmz_filename, forces_csv_filename=None, dt=0.01, keep_csv=True,
                 environment: Environment = None, thrust: Union[ThrustForce, List[ThrustForce]] = None):
        self.pitch = pitch
        self.yaw = yaw
        self.dt = dt
        self.csv_filename = csv_filename
        self.kmz_filename = kmz_filename
        self.keep_csv = keep_csv
        if environment is None:
            environment = Environment()
        self.environment = environment
        self.forces_csv_filename = forces_csv_filename
        self.thrust = thrust

    def launch(self, mass: float, position: Position, velocity=0, cross_section=lambda axis, pitch, yaw: 20,
               drag_coeff=lambda axis, pitch, yaw: 0.1):
        """
        Launch the projectile and fly it until it crashes.
        :param mass: projectile mass
        :param position: initial position
        :param velocity: initial velocity
        :param cross_section: cross section area
        :param drag_coeff: drag coefficient
        :return:
        """
        if self.forces_csv_filename is not None:
            forces_writer = ForcesCsvWriter(self.forces_csv_filename)
            forces_writer.write_header()
        else:
            forces_writer = None
        projectile = self.environment.create_projectile(mass, position, cross_section, drag_coeff, forces_writer)
        projectile.launch_at_angle(self.pitch, self.yaw, velocity)
        if self.thrust is not None:
            if isinstance(self.thrust, list):
                for th in self.thrust:
                    projectile.add_thrust(th)
            else:
                projectile.add_thrust(self.thrust)

        writer = ProjectileCsvWriter(self.csv_filename)
        writer.write_header()
        while True:
            projectile.advance(self.dt)
            data = projectile.get_state()
            writer.write_data(data)
            if projectile.has_hit_ground():
                break
        writer.close()
        if forces_writer is not None:
            forces_writer.close()

        convert_csv_to_kmz(self.csv_filename, self.kmz_filename)
        if not self.keep_csv:
            os.remove(self.csv_filename)
