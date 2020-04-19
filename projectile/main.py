import math

from projectile.Environment import Environment
from projectile.Position import Position

DT = 10**-2

if __name__ == '__main__':
    env = Environment()
    projectile = env.create_projectile(1, Position(0, 0, 0))
    projectile.launch_at_angle(math.pi/6, 0, 10.0)
    output = open("/home/luka/Documents/mehanika-seminarski/test.out", "w")
    while True:
        projectile.advance(DT)
        projectile.write_position(output)
        if projectile.has_hit_ground():
            break

    print("Finished!")
