from game.settings import *
import pygame


class Button:
    def __init__(self, x, y, width, height, text, screen, button_id):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.screen = screen
        self.button_id = button_id
        self.hovered = False
        self.clicked = False
        self.font = pygame.font.SysFont('microsoftyahei', 50)
        self.text_surface = self.font.render(text, True, YELLOW)

    def update(self, mouse_pos, mouse_clicked):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.clicked = self.hovered and mouse_clicked
        return self.clicked

    def render(self):
        # Base colors
        if self.clicked:
            bg_color = (80, 20, 20)  # Dark red
            border_color = RED
            text_color = WHITE
        elif self.hovered:
            bg_color = (20, 60, 20)  # Dark green
            border_color = GREEN
            text_color = YELLOW
        else:
            bg_color = (40, 40, 40)  # Dark gray
            border_color = (100, 100, 100)  # Light gray
            text_color = YELLOW

        # Draw button with border
        # Outer border
        border_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 2,
                                  self.rect.width + 4, self.rect.height + 4)
        pygame.draw.rect(self.screen, border_color, border_rect, border_radius=8)

        # Main button background
        pygame.draw.rect(self.screen, bg_color, self.rect, border_radius=5)

        # Re-render text with current color if needed
        if self.clicked or self.hovered:
            text_surface = self.font.render(self.text, True, text_color)
        else:
            text_surface = self.text_surface

        # Center and draw text
        text_rect = text_surface.get_rect()
        text_rect.center = self.rect.center
        self.screen.blit(text_surface, text_rect)
