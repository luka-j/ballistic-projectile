import zipfile
from datetime import datetime, timedelta
from math import degrees
from typing import Text

from projectile.data.CsvReader import CsvReader
from projectile.data.DataPoint import DataPoint
from projectile.data.ZipIO import compress
from projectile.util import fp_gt


def convert_csv_to_kmz(csv_name: str, kml_name: str):
    kml = KmlWriter(kml_name + ".kml")
    csv = CsvReader(csv_name)
    kml.convert(csv, sample_rate=10)
    compress(kml_name + ".kml", kml_name + ".kmz", zipfile.ZIP_DEFLATED, "doc.kml")


class KmlWriter:
    def __init__(self, filename: Text, peak_band=0.2, fuel_band=10, altitude_mode="absolute"):
        self.file = open(filename, "w")
        self.date = datetime.now()
        self.peak_band = peak_band
        self.fuel_band = fuel_band
        self.altitude_mode = altitude_mode
        self.wrote_peak = False
        self.wrote_fuel = False
        self.previous = None

    def write_header(self, name="flight"):
        self.file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        self.file.write("<kml xmlns='http://earth.google.com/kml/2.2'>\n")
        self.file.write("<Document>\n")
        self.file.write("   <name>{}</name>\n".format(name))
        self.write_styles()

    def write_styles(self):
        self.file.write("<Style id=\"peak\"><PolyStyle><color>ff0080ff</color></PolyStyle></Style>\n")
        self.file.write("<Style id=\"fuel\"><PolyStyle><color>ff0000ff</color></PolyStyle></Style>\n")

    def write(self, data: DataPoint, pretty=False):
        if self.previous is None:
            self.previous = data
            return

        time = self.date + timedelta(seconds=data.time)

        if pretty:
            self.file.write("<Placemark>\n")
            self.file.write("    <TimeSpan>\n        <begin>{}</begin>\n    </TimeSpan>\n".format(time.isoformat()))
            if self.fuel_band > data.z_speed > -self.fuel_band or (data.z_speed <= 0 and not self.wrote_peak):
                self.file.write("    <styleUrl>#peak</styleUrl>\n")
                self.wrote_peak = True
            if 0 < data.remaining_fuel <= self.fuel_band or (data.remaining_fuel == 0 and not self.wrote_fuel):
                self.file.write("    <styleUrl>#fuel</styleUrl>\n")
                self.wrote_fuel = True
            self.file.write("    <LineString>\n")
            self.file.write("        <extrude>1</extrude>\n")
            self.file.write("        <altitudeMode>{}</altitudeMode>\n".format(self.altitude_mode))
            self.file.write("        <coordinates>{},{},{} {},{},{}</coordinates>\n"
                            .format(degrees(self.previous.longitude), degrees(self.previous.latitude),
                                    self.previous.altitude, degrees(data.longitude), degrees(data.latitude), data.altitude))
            self.file.write("    </LineString>\n")
        else:
            self.file.write("<Placemark>")
            self.file.write("<TimeSpan><begin>{}</begin></TimeSpan>".format(time.isoformat()))
            if self.fuel_band > data.z_speed > -self.fuel_band or (data.z_speed <= 0 and not self.wrote_peak):
                self.file.write("<styleUrl>#peak</styleUrl>")
                self.wrote_peak = True
            if 0 < data.remaining_fuel <= self.fuel_band or (data.remaining_fuel == 0 and not self.wrote_fuel):
                self.file.write("<styleUrl>#fuel</styleUrl>")
                self.wrote_fuel = True
            self.file.write("<LineString>")
            self.file.write("<extrude>1</extrude>")
            self.file.write("<altitudeMode>{}</altitudeMode>".format(self.altitude_mode))
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
