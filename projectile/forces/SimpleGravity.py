from projectile.forces.Force import Force


class SimpleGravity(Force):
    """
    Defines normal, crude gravity. Assume gravity has constant acceleration in z-direction
    """
    def __init__(self):
        super().__init__(lambda pr: 0, lambda pr: 0, lambda pr: -9.81*pr.mass)
