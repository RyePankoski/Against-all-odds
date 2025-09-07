from game.settings import *


class Camera:
    def __init__(self, screen):
        self.viewport_width = CAMERA_VIEW_WIDTH
        self.viewport_height = CAMERA_VIEW_HEIGHT

        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.scale_x = self.screen_width / self.viewport_width
        self.scale_y = self.screen_height / self.viewport_height

        self.screen = screen

        # Camera position in world coordinates
        self.x = 0
        self.y = 0

        # Optional: smooth camera movement
        self.smoothing = 0.1

    def follow_target(self, target_x, target_y):
        # Use viewport size for camera positioning
        desired_x = target_x - self.viewport_width // 2
        desired_y = target_y - self.viewport_height // 2

        desired_x = max(0, min(desired_x, self.world_width - self.viewport_width))
        desired_y = max(0, min(desired_y, self.world_height - self.viewport_height))

        self.x = desired_x
        self.y = desired_y

    def world_to_screen(self, world_x, world_y):
        # Convert to viewport coordinates first
        viewport_x = world_x - self.x
        viewport_y = world_y - self.y

        # Then scale to screen coordinates
        screen_x = viewport_x * self.scale_x
        screen_y = viewport_y * self.scale_y
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        # Scale screen coordinates to viewport coordinates
        viewport_x = screen_x / self.scale_x
        viewport_y = screen_y / self.scale_y

        # Then convert viewport to world coordinates
        world_x = viewport_x + self.x
        world_y = viewport_y + self.y
        return world_x, world_y

    def is_visible(self, world_x, world_y, margin=50):
        # Check against viewport size, not screen size
        viewport_x = world_x - self.x
        viewport_y = world_y - self.y
        return (-margin <= viewport_x <= self.viewport_width + margin and
                -margin <= viewport_y <= self.viewport_height + margin)
