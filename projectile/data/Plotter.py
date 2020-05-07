from projectile.data.CsvReaders import ForcesCsvReader
import matplotlib.pyplot as plt
import numpy as np


def extract_force(reader: ForcesCsvReader, index: int):
    point = reader.read()
    force_data = []
    while point is not None:
        force_data.append([point.time, point.mass, *point.forces[index]])
        point = reader.read()
    reader.close()
    return np.array(force_data)


def simple_force_plot(reader: ForcesCsvReader, index: int, title: str):
    data = extract_force(reader, index).transpose()
    plt.title(title)
    plt.plot(data[0], data[2]/data[1], 'r', label="X")
    plt.plot(data[0], data[3]/data[1], 'g', label="Y")
    plt.plot(data[0], data[4]/data[1], 'b', label="Z")
    plt.show()
