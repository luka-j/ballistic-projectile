from projectile.core.Environment import Environment
from projectile.forces.ThrustForce import ThrustForce
from projectile.scenarios import run
from projectile.data.KmlWriter import convert_csv_to_kmz
import sys

"""
This script only does cmd argument parsing. Valid arguments:
run  - start a scenario (see scenarios.py)
plot - create a plot of forces from a Forces CSV
kmz  - convert Projectile CSV to KMZ format
"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("USAGE: <command> <argument> [...]")
        print("<command> is 'run', 'plot' or 'kmz'")
        exit(1)

    if sys.argv[1] == "run":
        run(sys.argv[2])
        print("Done!")
    elif sys.argv[1] == "plot":
        env = Environment()
        if not (len(sys.argv) > 3 and sys.argv[3] == "nothrust"):
            env.add_force(ThrustForce(1, lambda x: 0, 0, 0, 0))
        env.plot_all_forces(sys.argv[2])
    elif sys.argv[1] == "kmz":
        convert_csv_to_kmz(sys.argv[2], sys.argv[2].rsplit(".", 2)[1])
    else:
        print("Invalid command {}".format(sys.argv[1]))
        exit(1)
