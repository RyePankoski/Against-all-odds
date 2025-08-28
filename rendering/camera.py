import pygame
import math
from game.settings import *


class Camera:
    def __init__(self, screen):
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT
        self.screen = screen

        # Camera position in world coordinates
        self.x = 0
        self.y = 0

        # Optional: smooth camera movement
        self.smoothing = 0.1

    def follow_target(self, target_x, target_y):
        """Make camera follow a target (like the player)"""
        # Center camera on target
        desired_x = target_x - self.screen_width // 2
        desired_y = target_y - self.screen_height // 2

        # Keep camera within world bounds
        desired_x = max(0, min(desired_x, self.world_width - self.screen_width))
        desired_y = max(0, min(desired_y, self.world_height - self.screen_height))

        # Option 1: Instant camera (no smoothing)
        self.x = desired_x
        self.y = desired_y

        # Option 2: Smooth camera (uncomment to use)
        self.x += (desired_x - self.x) * self.smoothing
        self.y += (desired_y - self.y) * self.smoothing

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return world_x, world_y

    def is_visible(self, world_x, world_y, margin=50):
        """Check if a world position is visible on screen (with margin)"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return (-margin <= screen_x <= self.screen_width + margin and
                -margin <= screen_y <= self.screen_height + margin)
