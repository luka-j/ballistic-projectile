from typing import Text

from projectile.data.DataPoint import DataPoint
from math import degrees
from datetime import datetime, timedelta


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

    def write(self, data: DataPoint):
        if self.previous is None:
            self.previous = data
            return

        time = self.date + timedelta(seconds=data.time)

        self.file.write("<Placemark>\n")
        self.file.write("    <TimeSpan>\n        <begin>{}</begin>\n    </TimeSpan>\n"
                        .format(time.isoformat()))
        self.file.write("    <LineString>\n")
        self.file.write("        <extrude>1</extrude>\n")
        self.file.write("        <altitudeMode>relativeToGround</altitudeMode>\n")
        self.file.write("        <coordinates>{},{},{} {},{},{}</coordinates>\n"
                        .format(degrees(self.previous.longitude), degrees(self.previous.latitude),
                                self.previous.altitude, degrees(data.longitude), degrees(data.latitude), data.altitude))
        self.file.write("    </LineString>\n")
        self.file.write("</Placemark>\n")
        self.previous = data

    def close(self):
        self.file.write("</Document>\n")
        self.file.write("</kml>\n")
        self.file.close()
