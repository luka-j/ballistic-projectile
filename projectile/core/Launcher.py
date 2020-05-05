import os

from projectile.core.Environment import Environment
from projectile.core.Position import Position
from projectile.core.Projectile import Projectile
from projectile.data.CsvWriters import ProjectileCsvWriter, ForcesCsvWriter
from projectile.data.KmlWriter import convert_csv_to_kmz
from projectile.forces.ThrustForce import follow_path, ThrustForce
from projectile.util import spherical_to_planar_coord


def default_fuel_flow(t: float):
    if t < 2:
        return 600
    return 100


class Launcher:
    def default_thrust_direction(self, axis: int, force: float, pr: Projectile):
        if pr.time < 2:
            return spherical_to_planar_coord(axis, force, self.pitch, self.yaw)
        if pr.pitch < 0.15:
            spherical_to_planar_coord(axis, force, self.pitch + 0.17, self.yaw)
        return follow_path(axis, force, pr)

    def __init__(self, pitch, yaw, csv_filename, kmz_filename, forces_csv_filename=None, dt=0.01, keep_csv=True,
                 environment: Environment = None, thrust: ThrustForce = None):
        self.pitch = pitch
        self.yaw = yaw
        self.dt = dt
        self.csv_filename = csv_filename
        self.kmz_filename = kmz_filename
        self.keep_csv = keep_csv
        if environment is None:
            environment = Environment()
        self.environment = environment
        if thrust is None:
            thrust = ThrustForce(1800, default_fuel_flow, 100, 150000, 5, self.default_thrust_direction)
        self.forces_csv_filename = forces_csv_filename
        self.thrust = thrust

    def launch(self, mass: float, position: Position, velocity=0, cross_section=lambda axis, pitch, yaw: 20,
               drag_coeff=lambda axis, pitch, yaw: 0.1):
        if self.forces_csv_filename is not None:
            forces_writer = ForcesCsvWriter(self.forces_csv_filename)
            forces_writer.write_header()
        else:
            forces_writer = None
        projectile = self.environment.create_projectile(mass, position, cross_section, drag_coeff, forces_writer)
        projectile.launch_at_angle(self.pitch, self.yaw, velocity)
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
