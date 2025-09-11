import pygame
from ui_components.input_box import InputBox


class JoinLobbyWindow:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = pygame.display.get_desktop_sizes()[0]

        # Centered input box
        self.ip_box = InputBox(self.width / 2 - 100, self.height / 2 - 50, 200, 100, screen)
        self.name_box = InputBox(self.width / 2 - 100, self.height / 2 - 200, 200, 100, screen)
        self.number = None
        self.name = None
        self.open = True

    def run(self, dt, events):
        self.ip_box.update(dt, events)
        self.name_box.update(dt, events)

        self.ip_box.draw()
        self.name_box.draw()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                try:
                    self.number = self.ip_box.text
                    self.name = self.name_box.text
                except ValueError:
                    print("Invalid input, not a number")
