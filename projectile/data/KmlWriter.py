import zipfile
from datetime import datetime, timedelta
from math import degrees
from typing import Text

from projectile.data.CsvReaders import ProjectileCsvReader
from projectile.data.DataPoints import ProjectileDataPoint
from projectile.data.ZipIO import compress
from projectile.util import fp_gt


def convert_csv_to_kmz(csv_name: str, kml_name: str):
    """
    Converts a Projectile CSV file to KMZ file which can then be loaded to e.g. Google Earth.
    :param csv_name: filename of projectile CSV file (with extension)
    :param kml_name: filename of KMZ file to be created - WITHOUT extension
    :return:
    """
    kml = KmlWriter(kml_name + ".kml")
    csv = ProjectileCsvReader(csv_name)
    kml.convert(csv, sample_rate=10)
    compress(kml_name + ".kml", kml_name + ".kmz", zipfile.ZIP_DEFLATED, "doc.kml", False)


class KmlWriter:
    """
    Write projectile flight to a KML file which can be loaded to e.g. Google Eath
    (can be zipped and then becomes KMZ file).
    """
    def __init__(self, filename: Text, peak_band=10, fuel_band=60, altitude_mode="absolute"):
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
        self.file.write(f"   <name>{name}</name>\n")
        self.write_styles()

    def write_styles(self):
        self.file.write("<Style id=\"peak\"><PolyStyle><color>ff0080ff</color></PolyStyle></Style>\n")
        self.file.write("<Style id=\"fuel\"><PolyStyle><color>ff0000ff</color></PolyStyle></Style>\n")

    def write(self, data: ProjectileDataPoint, pretty=False):
        if self.previous is None:
            self.previous = data
            return

        time = self.date + timedelta(seconds=data.time)

        if pretty:
            self.file.write("<Placemark>\n")
            self.file.write(f"    <TimeSpan>\n        <begin>{time.isoformat()}</begin>\n    </TimeSpan>\n")
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
            self.file.write(f"<TimeSpan><begin>{time.isoformat()}</begin></TimeSpan>")
            if self.peak_band > data.z_speed > -self.peak_band or (data.z_speed <= 0 and not self.wrote_peak):
                self.file.write("<styleUrl>#peak</styleUrl>")
                self.wrote_peak = True
            if 0 < data.remaining_fuel <= self.fuel_band or (data.remaining_fuel == 0 and not self.wrote_fuel):
                self.file.write("<styleUrl>#fuel</styleUrl>")
                self.wrote_fuel = True
            self.file.write("<LineString>")
            self.file.write("<extrude>1</extrude>")
            self.file.write(f"<altitudeMode>{self.altitude_mode}</altitudeMode>")
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

    def convert(self, reader: ProjectileCsvReader, name="flight", sample_rate=100, speed_factor=1):
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
