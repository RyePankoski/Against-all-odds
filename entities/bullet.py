from core.settings import *


class Bullet:
    def __init__(self, x, y, dx, dy, angle, owner, true_angle):
        self.x = x
        self.y = y
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
        self.x += self.dx + (self.true_dx * self.velocity)
        self.y += self.dy + (self.true_dy * self.velocity)
        self.sector = self.x // SECTOR_SIZE, self.y // SECTOR_SIZE

    def check_for_collisions(self, ships, asteroids):
        for ship in ships:
            if ship.owner == self.owner:
                continue

            distance_squared = ((ship.x - self.x) * (ship.x - self.x) + (ship.y - self.y) * (ship.y - self.y))

            if distance_squared < BULLET_HIT_RANGE * BULLET_HIT_RANGE:

                if ship.shield > 0:
                    ship.shield -= 10
                    if ship.shield < 0:
                        ship.shield = 0

                self.alive = False
                return

        if self.sector in asteroids and asteroids[self.sector]:
            for asteroid in asteroids[self.sector]:

                distance_squared = ((((asteroid.x - self.x) * (asteroid.x - self.x)) +
                                     ((asteroid.y - self.y) * (asteroid.y - self.y))) -
                                    (asteroid.radius * asteroid.radius))

                if distance_squared < BULLET_HIT_RANGE * BULLET_HIT_RANGE:
                    self.alive = False
                    return
