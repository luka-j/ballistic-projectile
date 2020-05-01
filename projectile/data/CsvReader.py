from typing import Text

from projectile.data.DataPoint import DataPoint


class CsvReader:
    def __init__(self, filename: Text):
        self.file = open(filename, "r")
        self.read_lines = 0

    def read(self):
        if self.read_lines == 0:
            line = self.file.readline()
        line = self.file.readline()
        self.read_lines += 1
        if line == "":
            return None
        line = line.split(",")
        return DataPoint(float(line[0]), float(line[1]), float(line[2]), float(line[3]), float(line[4]), float(line[5]),
                         float(line[6]), float(line[7]), float(line[8]), float(line[9]), float(line[10].strip()))

    def close(self):
        self.file.close()
