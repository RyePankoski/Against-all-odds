import pygame
import os
from pathlib import Path


class SpriteManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpriteManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not SpriteManager._initialized:
            self.sprites = {}
            self.base_path = Path(__file__).parent.parent
            self.load_sprites()
            SpriteManager._initialized = True

    def load_sprites(self):
        sprite_paths = {
            'ship1': 'ship_sprites/ship1.png',
            'ship2': 'ship_sprites/ship2.png',
            'aiShip': 'ship_sprites/aiShip.png',
            'aiShip2': 'ship_sprites/aiShip2.png',
            'aiShip3': 'ship_sprites/aiShip3.png',
            'aiShip4': 'ship_sprites/aiShip.png',
            'rocket': 'weapon_sprites/rocket.png',
            'bullet': 'weapon_sprites/bullet.png',
            "battleship": 'ship_sprites/battle_ship.png',
        }

        for name, relative_path in sprite_paths.items():
            full_path = self.base_path / relative_path
            try:
                if full_path.exists():
                    sprite = pygame.image.load(str(full_path)).convert_alpha()
                    self.sprites[name] = sprite
                    print(f"Loaded sprite: {name}")
                else:
                    print(f"Sprite file not found: {full_path}")
                    self.sprites[name] = None
            except pygame.error as e:
                print(f"Error loading sprite {name}: {e}")
                self.sprites[name] = None

    @classmethod
    def get_sprite(cls, name):
        instance = cls()
        return instance.sprites.get(name, None)

    @classmethod
    def get_rotated_sprite(cls, name, angle):
        sprite = cls.get_sprite(name)
        if sprite:
            return pygame.transform.rotate(sprite, angle)
        return None

    @classmethod
    def reload_sprites(cls):
        if cls._instance:
            cls._instance.load_sprites()
