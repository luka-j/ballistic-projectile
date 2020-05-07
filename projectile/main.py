import math

from projectile.core.Environment import Environment
from projectile.core.Launcher import Launcher
from projectile.core.Position import Position

if __name__ == '__main__':
    env = Environment(surface_altitude=lambda p: 77)
    launcher = Launcher(math.pi / 4, math.pi/3, "test.csv", "test", "forces.csv", environment=env)
    launcher.launch(8000, Position(math.radians(80), math.radians(24), 77))

    print("Launch finished, plotting...")
    env.plot_all_forces("forces.csv")

    print("Done!")
