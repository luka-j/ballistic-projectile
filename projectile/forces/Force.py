from projectile.Constants import X_INDEX, Y_INDEX, Z_INDEX
from projectile.Projectile import Projectile


class Force:
    intensity = [lambda pr: 0, lambda pr: 0, lambda pr: 0]

    def __init__(self, x, y, z):
        self.intensity[X_INDEX] = x
        self.intensity[Y_INDEX] = y
        self.intensity[Z_INDEX] = z

    def get_x(self, projectile: Projectile):
        return self.intensity[X_INDEX](projectile)

    def get_y(self, projectile: Projectile):
        return self.intensity[Y_INDEX](projectile)

    def get_z(self, projectile: Projectile):
        return self.intensity[Z_INDEX](projectile)

    def get(self, axis):
        return self.intensity[axis]
