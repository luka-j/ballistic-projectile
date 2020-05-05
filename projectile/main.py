import math

from projectile.core.Environment import Environment
from projectile.core.Launcher import Launcher
from projectile.core.Position import Position

if __name__ == '__main__':
    launcher = Launcher(math.pi / 4, math.pi/2, "test.csv", "test", "forces.csv",
                        environment=Environment(surface_altitude=lambda p: 77))
    launcher.launch(8000, Position(math.radians(80), math.radians(24), 77))

    print("Finished!")
