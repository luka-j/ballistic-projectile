from typing import Text

from projectile.data.CsvReader import CsvReader
from projectile.data.DataPoint import DataPoint
from math import degrees
from datetime import datetime, timedelta
from projectile.util import fp_gt


class KmlWriter:
    def __init__(self, filename: Text):
        self.file = open(filename, "w")
        self.date = datetime.now()
        self.previous = None

    def write_header(self, name="flight"):
        self.file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        self.file.write("<kml xmlns='http://earth.google.com/kml/2.2'>\n")
        self.file.write("<Document>\n")
        self.file.write("   <name>{}</name>\n".format(name))

    def write(self, data: DataPoint, pretty=False):
        if self.previous is None:
            self.previous = data
            return

        time = self.date + timedelta(seconds=data.time)

        self.file.write("<Placemark>\n")
        if pretty:
            self.file.write("    <TimeSpan>\n        <begin>{}</begin>\n    </TimeSpan>\n"
                            .format(time.isoformat()))
            self.file.write("    <LineString>\n")
            self.file.write("        <extrude>1</extrude>\n")
            self.file.write("        <altitudeMode>relativeToGround</altitudeMode>\n")
            self.file.write("        <coordinates>{},{},{} {},{},{}</coordinates>\n"
                            .format(degrees(self.previous.longitude), degrees(self.previous.latitude),
                                    self.previous.altitude, degrees(data.longitude), degrees(data.latitude), data.altitude))
            self.file.write("    </LineString>\n")
        else:
            self.file.write("<TimeSpan><begin>{}</begin></TimeSpan>"
                            .format(time.isoformat()))
            self.file.write("<LineString>")
            self.file.write("<extrude>1</extrude>")
            self.file.write("<altitudeMode>relativeToGround</altitudeMode>")
            self.file.write("<coordinates>{},{},{} {},{},{}</coordinates>"
                            .format(degrees(self.previous.longitude), degrees(self.previous.latitude),
                                    self.previous.altitude, degrees(data.longitude), degrees(data.latitude),
                                    data.altitude))
            self.file.write("</LineString>")
        self.file.write("</Placemark>\n")
        self.previous = data

    def close(self):
        self.file.write("</Document>\n")
        self.file.write("</kml>\n")
        self.file.close()

    def convert(self, reader: CsvReader, name="flight", sample_rate=100, speed_factor=1):
        dt = 1/sample_rate
        offset = 0
        self.write_header(name)
        data = reader.read()
        self.write(data)
        new_data = reader.read()
        while new_data is not None:
            new_data.time -= offset
            while new_data is not None and fp_gt(data.time + dt, new_data.time):
                new_data = reader.read()
            if new_data is None:
                break
            offset += (new_data.time - data.time) * (1 - 1/speed_factor)
            new_data.time -= (new_data.time - data.time) * (1 - 1/speed_factor)

            data = new_data
            self.write(data)
            new_data = reader.read()
        self.close()
