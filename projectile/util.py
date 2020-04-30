from math import fabs


def sgn(x) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def fp_eq(x: float, y: float) -> bool:
    return fabs(x-y) < 10**-12


def fp_lt(x: float, y: float) -> bool:
    return not fp_eq(x, y) and x < y


def fp_gt(x: float, y: float) -> bool:
    return not fp_eq(x, y) and x > y
