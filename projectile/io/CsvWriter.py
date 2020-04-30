from typing import Text

from projectile.io.DataPoint import DataPoint


class CsvWriter:
    def __init__(self, filename: Text):
        self.file = open(filename, "w")

    def write_header(self):
        self.file.write("time,distance,latitude,longitude,altitude,Vx,Vy,Vz,pitch,yaw\n")

    def write_data(self, data: DataPoint):
        self.file.write("{:.4f},{:.2f},{},{},{},{},{},{},{},{}\n".format(data.time, data.planar_distance, data.latitude,
                                                                         data.longitude, data.altitude, data.x_speed,
                                                                         data.y_speed, data.z_speed, data.pitch,
                                                                         data.yaw))

    def close(self):
        self.file.close()
