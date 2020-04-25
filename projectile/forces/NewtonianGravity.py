from projectile.forces.Force import Force

G = 6.674e-11


class NewtonianGravity(Force):
    def __init__(self, distance_to_earths_center=6378137, earth_mass=5.97237e24):
        super().__init__(lambda p, env: 0, lambda p, env: 0,
                         lambda p, env: -G*earth_mass*p.mass(p.time)/distance_to_earths_center**2)
