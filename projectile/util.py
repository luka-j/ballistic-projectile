import time

from collections import deque
from math import fabs, sqrt, sin, cos, asin

from projectile.core.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.core.Position import Position


def sgn(x) -> int:
    """Sign of the number; -1, 0 or 1"""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def fp_eq(x: float, y: float) -> bool:
    """Whether two floating point numbers are equal. Epsilon = 10^-12"""
    return fabs(x-y) < 10**-12


def fp_lt(x: float, y: float) -> bool:
    """Whether one floating point is lesser than the other and not equal."""
    return not fp_eq(x, y) and x < y


def fp_gt(x: float, y: float) -> bool:
    """Whether one floating point is lesser than the other and not equal."""
    return not fp_eq(x, y) and x > y


def haversine(pos1: Position, pos2: Position, radius: float) -> float:
    """Haversine formula. Distance between two lat/lon points in meters."""
    dlon = pos2.lon - pos1.lon
    dlat = pos2.lat - pos1.lat
    a = sin(dlat/2)**2 + cos(pos1.lat) * cos(pos2.lat) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * radius


def spherical_to_planar_coord(axis: int, intensity: float, pitch: float, yaw: float) -> float:
    """Convert spherical coordinates (pitch/yaw) to planar, with specified intensity."""
    if axis == X_INDEX:
        return intensity * cos(yaw) * cos(pitch)
    if axis == Y_INDEX:
        return intensity * sin(yaw) * cos(pitch)
    if axis == Z_INDEX:
        return intensity * sin(pitch)


class RollingStatistic:
    """Calculates rolling mean and standard deviation."""
    PRINT_WARNINGS = False
    PRINT_DEBUG = False

    def __init__(self, window_size, ready_threshold=5):
        self.N = window_size
        self.ready_threshold = ready_threshold
        self.mean = 0
        self.variance = 0
        self.stddev = 0
        self.elements = deque(maxlen=self.N)
        self.filled = 0

    def update(self, new) -> None:
        if self.filled < self.N:
            oldavg = self.mean
            self.mean = (self.mean * self.filled + new) / (self.filled + 1)
            if self.filled >= 1:
                self.variance = ((self.filled-1)/self.filled) * self.variance + 1/(self.filled+1)*((new-oldavg)**2)
                self.stddev = sqrt(self.variance)
            self.elements.append(new)
            self.filled += 1
        else:
            old = self.elements.popleft()
            oldavg = self.mean
            self.mean = oldavg + (new - old) / self.N
            newvar = self.variance + (new-old) * (new - self.mean + old - oldavg) / (self.N - 1)
            if newvar < 0 and RollingStatistic.PRINT_WARNINGS:
                print("Warning: Variance underflow!")
            elif newvar > 0:
                self.variance = newvar
            if RollingStatistic.PRINT_DEBUG:
                print("New sample: {}, Mean: {}, variance: {}".format(new, self.mean, self.variance))
            self.stddev = sqrt(self.variance)
            self.elements.append(new)

    def is_outlier(self, sample, stddev_threshold=2) -> bool:
        if self.filled < self.ready_threshold:
            return False
        return fabs(sample - self.mean) > self.stddev*stddev_threshold


class Stopwatch:
    """Measures and prints elapsed time between start and lap/stop."""
    def __init__(self):
        self.start_time = 0
        self.total_time = 0
        self.lap_count = 0

    def start(self) -> None:
        self.start_time = time.time()

    def lap(self) -> None:
        lap_time = time.time() - self.start_time
        self.total_time += lap_time
        self.lap_count += 1
        print("Lap {}: {}, total: {}".format(self.lap_count, lap_time, self.total_time))
        self.start_time = time.time()

    def stop(self) -> None:
        self.total_time += (time.time() - self.start_time)
        print("Execution finished. Total time: {}".format(self.total_time))
