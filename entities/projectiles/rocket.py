from game.settings import *
import pygame
from rendering.sprite_manager import SpriteManager
from entities.projectiles.projectile import Projectile


class Rocket(Projectile):
    def __init__(self, x, y, dx, dy, angle, owner, true_angle):
        super().__init__()

        self.name = "rocket"
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
        self.fuel = ROCKET_FUEL
        self.alive = True

        screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
        scale_x = screen_width / CAMERA_VIEW_WIDTH
        scale_y = screen_height / CAMERA_VIEW_HEIGHT

        original_sprite = SpriteManager.get_sprite('rocket')
        if original_sprite:
            scaled_width = int(original_sprite.get_width() * scale_x)
            scaled_height = int(original_sprite.get_height() * scale_y)
            self.scaled_sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
        else:
            self.scaled_sprite = None

    def run(self):
        self.fly()

    def fly(self):
        if self.fuel > 0:
            self.velocity += ROCKET_THRUST
            self.fuel -= 1

        self.prev_x = self.x
        self.prev_y = self.y

        self.x += self.dx + (self.true_dx * self.velocity)
        self.y += self.dy + (self.true_dy * self.velocity)

        self.sector = self.x // SECTOR_SIZE, self.y // SECTOR_SIZE

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'prev_x': self.prev_x,
            'prev_y': self.prev_y,
            'dx': self.dx,
            'dy': self.dy,
            'true_dx': self.true_dx,
            'true_dy': self.true_dy,
            'alive': self.alive,
            'owner': str(self.owner) if self.owner else None,
            'sector': self.sector,
        }
