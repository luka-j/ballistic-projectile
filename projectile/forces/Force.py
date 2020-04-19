from projectile.Projectile import Projectile


class Force:
    X_INDEX = 0
    Y_INDEX = 1
    Z_INDEX = 2

    intensity = [lambda pr: 0, lambda pr: 0, lambda pr: 0]

    def __init__(self, x, y, z):
        self.intensity[self.X_INDEX] = x
        self.intensity[self.Y_INDEX] = y
        self.intensity[self.Z_INDEX] = z

    def get_x(self, projectile: Projectile):
        return self.intensity[self.X_INDEX](projectile)

    def get_y(self, projectile: Projectile):
        return self.intensity[self.Y_INDEX](projectile)

    def get_z(self, projectile: Projectile):
        return self.intensity[self.Y_INDEX](projectile)

    def get(self, axis):
        return self.intensity[axis]
