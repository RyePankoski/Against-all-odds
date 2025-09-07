from game.settings import *
import pygame
from rendering.sprite_manager import SpriteManager


class Bullet:
    def __init__(self, x, y, dx, dy, angle, owner, true_angle):
        self.name = "bullet"
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

        screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
        scale_x = screen_width / CAMERA_VIEW_WIDTH
        scale_y = screen_height / CAMERA_VIEW_HEIGHT

        original_sprite = SpriteManager.get_sprite('bullet')
        if original_sprite:
            scaled_width = int(original_sprite.get_width() * scale_x)
            scaled_height = int(original_sprite.get_height() * scale_y)
            self.scaled_sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
        else:
            self.scaled_sprite = None

    def update(self):
        self.fly()

    def fly(self):
        self.prev_x = self.x
        self.prev_y = self.y

        self.x += self.dx + (self.true_dx * self.velocity)
        self.y += self.dy + (self.true_dy * self.velocity)
        self.sector = self.x // SECTOR_SIZE, self.y // SECTOR_SIZE
