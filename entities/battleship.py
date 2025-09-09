from game.settings import *
import pygame
from rendering.sprite_manager import SpriteManager
import random
from entities.ship import Ship


class BattleShip(Ship):
    def __init__(self, x, y):
        super().__init__(x, y, -1, camera=None)
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.shield = 500
        self.health = 1000

        screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
        scale_x = screen_width / CAMERA_VIEW_WIDTH
        scale_y = screen_height / CAMERA_VIEW_HEIGHT
        sprite_name = 'battleship'
        original_sprite = SpriteManager.get_sprite(sprite_name)
        if original_sprite:
            scaled_width = int(original_sprite.get_width() * scale_x)
            scaled_height = int(original_sprite.get_height() * scale_y)
            self.ship_sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
        else:
            print("no sprite found")
            self.ship_sprite = None

    def run(self, dt=None):
        self.move()

    def move(self):
        self.x += self.dx * BS_THRUST
        self.y += self.dy * BS_THRUST

        if self.x > WORLD_WIDTH or self.x < 0:
            self.dx *= -1
        if self.y > WORLD_HEIGHT or self.y < 0:
            self.dy *= -1
