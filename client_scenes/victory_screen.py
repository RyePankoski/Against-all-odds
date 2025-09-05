import pygame.display
from game.settings import *
from ui_components.button import Button


class VictoryScreen:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = pygame.display.get_desktop_sizes()[0]
        button_width = 500
        button_width_offset = button_width / 2
        button_height = 100

        self.buttons = []

        new_game_button = Button(self.width / 2 - button_width_offset, self.height / 2, button_width,
                                 button_height, "NEW_GAME?", self.screen, "new_game_button")
        self.buttons.append(new_game_button)

        self.state_to_extract = None

    def run(self):
        self.render()
        self.handle_buttons()

    def handle_buttons(self):
        mouse_buttons = pygame.mouse.get_pressed()
        left_clicked = mouse_buttons[0]
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            clicked = button.update(mouse_pos, left_clicked)
            button.render()

            if clicked:
                if button.button_id == "new_game_button":
                    self.state_to_extract = "new_game"

    def render(self):
        pygame.draw.rect(self.screen, GRAY, (self.width // 2 - 500, self.height // 2 - 500, 1000, 1000))
