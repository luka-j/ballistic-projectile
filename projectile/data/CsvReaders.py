from typing import Text
import numpy as np

from projectile.data.DataPoints import ProjectileDataPoint, ForcesDataPoint


class ProjectileCsvReader:
    def __init__(self, filename: Text):
        self.file = open(filename, "r")
        self.read_lines = 0

    def read(self):
        if self.read_lines == 0:
            self.file.readline()  # read header and ignore
        line = self.file.readline()
        self.read_lines += 1
        if line == "":
            return None
        line = line.split(",")
        return ProjectileDataPoint(float(line[0]), float(line[1]), float(line[2]), float(line[3]), float(line[4]),
                                   float(line[5]), float(line[6]), float(line[7]), float(line[8]), float(line[9]),
                                   float(line[10].strip()))

    def close(self):
        self.file.close()


class ForcesCsvReader:
    def __init__(self, filename: Text):
        self.file = open(filename, "r")
        self.prev_line = None
        self.read_lines = 0

    def read(self):
        if self.read_lines == 0:
            self.file.readline()  # read header and ignore
        if self.prev_line is None:
            line = self.file.readline().split(",")
        else:
            line = self.prev_line
        self.read_lines += 1
        if line == [""] or line == "":
            return None
        time, mass = float(line[0]), float(line[1])
        force_i = -1
        forces = []
        while line != [""] and float(line[2]) > force_i:
            forces.append([float(line[3]), float(line[4]), float(line[5])])
            line = self.file.readline().split(",")
            self.prev_line = line
            force_i += 1
        if line == [""] or line == "":
            return None
        return ForcesDataPoint(time, mass, np.array(forces))

    def close(self):
        self.file.close()
