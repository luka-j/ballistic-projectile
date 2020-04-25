from projectile.forces.Force import Force


class SimpleGravity(Force):
    """
    Defines simple, crude gravity. Assume gravity has constant acceleration in z-direction
    """
    def __init__(self):
        self.intensity = [0, 0, 0]
        super().__init__(lambda pr, env: 0, lambda pr, env: 0, lambda pr, env: -9.81*pr.mass(pr.time))
