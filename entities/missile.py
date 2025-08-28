from game.settings import *


class Missile:
    def __init__(self, x, y, dx, dy, angle, owner, true_angle):
        self.name = "missile"
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.dx = dx
        self.dy = dy

        self.true_dx, self.true_dy = true_angle
        self.angle = angle
        self.sector = 0

        self.owner = owner
        self.velocity = 0
        self.fuel = MISSILE_FUEL
        self.alive = True

    def update(self):
        self.fly()

    def fly(self):
        if self.fuel > 0:
            self.velocity += MISSILE_THRUST
            self.velocity += MISSILE_THRUST
            self.fuel -= 1

        self.prev_x = self.x
        self.prev_y = self.y

        self.x += self.dx + (self.true_dx * self.velocity)
        self.y += self.dy + (self.true_dy * self.velocity)

        self.sector = self.x // SECTOR_SIZE, self.y // SECTOR_SIZE


