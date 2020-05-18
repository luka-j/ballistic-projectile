X_INDEX: int = 0
Y_INDEX: int = 1
Z_INDEX: int = 2

DEBUG = False

"""Universal gas constant"""
R = 8.3144598
"""Gravitational constant"""
G = 6.674e-11


class DragCoefficients:
    """
    Drag coefficients for common shapes. Source: https://en.wikipedia.org/wiki/Drag_coefficient
    """
    SPHERE = 0.47
    HALF_SPHERE = 0.42
    CONE = 0.5
    CUBE = 1.05
    ANGLED_CUBE = 0.8
    LONG_CYLINDER = 0.82
    SHORT_CYLINDER = 1.15
    STREAMLINED_BODY = 0.04
    STREAMLINED_HALFBODY = 0.09


class Atmosphere:
    """
    Defines contract for defining atmospheres. Subclass this to define atmospheres.
    """
    def temp_lapse_rate(self, h: float) -> float:
        raise ValueError("Undefined atmosphere!")

    def mass_density(self, h: float) -> float:
        raise ValueError("Undefined atmosphere!")

    def base_temp(self, h: float) -> float:
        raise ValueError("Undefined atmosphere!")

    def atmosphere_layer_start(self, h: float) -> float:
        raise ValueError("Undefined atmosphere!")

    def molar_mass(self, h: float) -> float:
        raise ValueError("Undefined atmosphere!")


class StandardAtmosphere(Atmosphere):
    """
    Values correspond to U. S. Standard Atmosphere 1976
    """

    def temp_lapse_rate(self, h: float) -> float:
        """
        How much temperature lapses. K/m
        :param h: height
        :return: lapse rate at the specified height
        """
        if h < 11000: return -0.0065
        if h < 20000: return 0
        if h < 32000: return 0.001
        if h < 47000: return 0.0028
        if h < 51000: return 0
        if h < 71000: return -0.0028
        return -0.002

    def mass_density(self, h: float) -> float:
        """
        Base density for layer at specified height.
        :param h: height
        :return: base density used for barometric formula
        """
        if h < 11000: return 1.2250
        if h < 20000: return 0.36391
        if h < 32000: return 0.08803
        if h < 47000: return 0.01322
        if h < 51000: return 0.00143
        if h < 71000: return 0.00086
        return 0.000064

    def base_temp(self, h: float) -> float:
        """
        Base temperature for layer at specified height.
        :param h: height
        :return: base temperature used for barometric formula
        """
        if h < 11000: return 288.15
        if h < 20000: return 216.65
        if h < 32000: return 216.65
        if h < 47000: return 228.65
        if h < 51000: return 270.65
        if h < 71000: return 270.65
        return 214.65

    def atmosphere_layer_start(self, h: float) -> float:
        """
        Where the layer which encompasses this height starts. Always smaller than h.
        :param h: height
        :return: layer start height
        """
        if h < 11000: return 0
        if h < 20000: return 11000
        if h < 32000: return 20000
        if h < 47000: return 32000
        if h < 51000: return 47000
        if h < 71000: return 51000
        return 71000

    def molar_mass(self, h: float) -> float:
        """
        Molar mass of the atmosphere at the specified height. Constant.
        This is wrong for heights above 100km where molecular structure of the atmosphere starts to fall apart
        and molar mass changes.
        :param h: height, ignored
        :return: molar mass of the atmosphere (const)
        """
        return 0.0289644  # this is a lie above 100km
