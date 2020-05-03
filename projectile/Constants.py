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
