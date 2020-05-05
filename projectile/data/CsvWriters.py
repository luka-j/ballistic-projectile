from typing import Text

from projectile.data.DataPoints import ProjectileDataPoint, ForcesDataPoint
from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX


class ProjectileCsvWriter:
    def __init__(self, filename: Text):
        self.file = open(filename, "w")

    def write_header(self):
        self.file.write("time,distance,latitude,longitude,altitude,Vx,Vy,Vz,pitch,yaw,fuel\n")

    def write_data(self, data: ProjectileDataPoint):
        self.file.write("{:.4f},{:.2f},{},{},{},{},{},{},{},{},{:.2f}\n"
                        .format(data.time, data.planar_distance, data.latitude, data.longitude, data.altitude,
                                data.x_speed, data.y_speed, data.z_speed, data.pitch, data.yaw, data.remaining_fuel))

    def close(self):
        self.file.close()


class ForcesCsvWriter:
    def __init__(self, filename: Text):
        self.file = open(filename, "w")

    def write_header(self):
        self.file.write("time,mass,force_id,Fx,Fy,Fz\n")

    def write_data(self, data: ForcesDataPoint):
        i = 0
        for force in data.forces:
            self.file.write("{:.4f},{:.2f},{},{},{},{}\n".format(data.time, data.mass, i, force[X_INDEX],
                                                                 force[Y_INDEX], force[Z_INDEX]))
            i += 1

    def close(self):
        self.file.close()
