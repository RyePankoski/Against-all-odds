from game.settings import *


class Bullet:
    def __init__(self, x, y, dx, dy, angle, owner, true_angle):
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
        self.velocity = BULLET_SPEED
        self.alive = True

    def handle_self(self):
        self.fly()

    def fly(self):

        self.prev_x = self.x
        self.prev_y = self.y

        self.x += self.dx + (self.true_dx * self.velocity)
        self.y += self.dy + (self.true_dy * self.velocity)
        self.sector = self.x // SECTOR_SIZE, self.y // SECTOR_SIZE

