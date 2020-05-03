X_INDEX: int = 0
Y_INDEX: int = 1
Z_INDEX: int = 2

DEBUG = False

R = 8.3144598
G = 6.674e-11


class DragCoefficients:
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
    def temp_lapse_rate(self, h: float):
        raise ValueError("Undefined atmosphere!")

    def mass_density(self, h: float):
        raise ValueError("Undefined atmosphere!")

    def base_temp(self, h: float):
        raise ValueError("Undefined atmosphere!")

    def atmosphere_layer_start(self, h: float):
        raise ValueError("Undefined atmosphere!")

    def molar_mass(self, h: float):
        raise ValueError("Undefined atmosphere!")


class StandardAtmosphere(Atmosphere):
    def temp_lapse_rate(self, h: float):
        if h < 11000: return -0.0065
        if h < 20000: return 0
        if h < 32000: return 0.001
        if h < 47000: return 0.0028
        if h < 51000: return 0
        if h < 71000: return -0.0028
        return -0.002

    def mass_density(self, h: float):
        if h < 11000: return 1.2250
        if h < 20000: return 0.36391
        if h < 32000: return 0.08803
        if h < 47000: return 0.01322
        if h < 51000: return 0.00143
        if h < 71000: return 0.00086
        return 0.000064

    def base_temp(self, h: float):
        if h < 11000: return 288.15
        if h < 20000: return 216.65
        if h < 32000: return 216.65
        if h < 47000: return 228.65
        if h < 51000: return 270.65
        if h < 71000: return 270.65
        return 214.65

    def atmosphere_layer_start(self, h: float):
        if h < 11000: return 0
        if h < 20000: return 11000
        if h < 32000: return 20000
        if h < 47000: return 32000
        if h < 51000: return 47000
        if h < 71000: return 51000
        return 71000

    def molar_mass(self, h: float):
        return 0.0289644  # this is a lie above 100km
