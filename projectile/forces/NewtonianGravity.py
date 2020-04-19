from projectile.forces.Force import Force

G = 6.674 * 10**-11


class NewtonianGravity(Force):
    def __init__(self, distance_to_earths_center=6370*10**3, earth_mass=5.9722*10**24):
        super().__init__(lambda p: 0, lambda p: 0, lambda p: -G*earth_mass*p.mass/distance_to_earths_center**2)
