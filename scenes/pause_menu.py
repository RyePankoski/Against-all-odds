import pygame


def handle_input(keys):
    if keys[pygame.K_RETURN]:
        return "play"
    elif keys[pygame.K_ESCAPE]:
        return "quit"
    return None


class PauseMenu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    def render(self):
        self.screen.fill((0, 0, 50))

        # Just draw text directly
        play_text = self.font.render("Press ENTER to Play", True, (255, 255, 255))
        self.screen.blit(play_text, (300, 300))

        quit_text = self.font.render("Press ESC to Quit", True, (255, 255, 255))
        self.screen.blit(quit_text, (300, 350))
