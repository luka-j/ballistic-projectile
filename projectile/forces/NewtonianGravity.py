from projectile.core.Constants import G
from projectile.forces.Force import Force


class NewtonianGravity(Force):
    """
    Defines gravity as Newton did back in the day. Acts downwards.
    """
    def __init__(self, distance_to_earths_center=6378137, earth_mass=5.97237e24):
        super().__init__(lambda p, env: 0, lambda p, env: 0,
                         lambda p, env: -G*earth_mass*p.mass()/(distance_to_earths_center+p.position.alt)**2)
