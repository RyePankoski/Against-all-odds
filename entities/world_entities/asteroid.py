from game.settings import *


class Asteroid:
    def __init__(self, x, y, dx, dy, radius, world_dim, sector):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = radius
        self.world_dimensions = world_dim
        self.sector = sector
        self.health = self.radius * 1.5

        self.alive = True

    def float_on(self):
        self.x += self.dx
        self.y += self.dy

        if self.x > self.world_dimensions[0] + 150 or self.x < 0 - 150:
            self.alive = False
        if self.y > self.world_dimensions[1] + 150 or self.y < 0 - 150:
            self.alive = False

        self.sector = int(self.x // SECTOR_SIZE), int(self.y // SECTOR_SIZE)
