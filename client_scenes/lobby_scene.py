from rendering.sprite_manager import SpriteManager
from ui_components.button import Button
from game.settings import *

import pygame


class Lobby:
    def __init__(self, screen, network_layer):
        self.screen = screen
        self.network_layer = network_layer
        self.max_players = 10
        self.player_ready = False

        self.width, self.height = pygame.display.get_desktop_sizes()[0]
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.ship_sprite = SpriteManager.get_sprite("ship1")

        self.input_boxes = []
        self.buttons = []
        self.players = []
        self.init_components()

    def set_players(self, players):
        self.players = players

    def run(self, events):
        self.render()
        self.handle_buttons(events)

    def render(self):
        # Title
        title_text = self.title_font.render("Waiting for Players...", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width / 2, 100))
        self.screen.blit(title_text, title_rect)

        # Player count
        count_text = self.font.render(f"Players: {len(self.players)}/{self.max_players}", True, (200, 200, 200))
        count_rect = count_text.get_rect(center=(self.width / 2, 140))
        self.screen.blit(count_text, count_rect)

        # Players list with a simple border
        if self.players:
            list_y = 200
            list_width = 300
            list_height = len(self.players) * 50 + 20
            list_x = self.width / 2 - list_width / 2

            # Background box
            pygame.draw.rect(self.screen, (30, 30, 30),
                             (list_x - 10, list_y - 10, list_width + 20, list_height + 20))
            pygame.draw.rect(self.screen, (100, 100, 100),
                             (list_x - 10, list_y - 10, list_width + 20, list_height + 20), 2)

            for i, player in enumerate(self.players):
                y_pos = list_y + i * 50

                # Ship sprite
                self.screen.blit(self.ship_sprite, (list_x, y_pos))

                # Player name
                text_surf = self.font.render(player, True, (255, 255, 255))
                self.screen.blit(text_surf, (list_x + 60, y_pos + 10))

                # Ready indicator
                pygame.draw.circle(self.screen, RED,
                                   (int(list_x + list_width - 20), int(y_pos + 20)), 5)

    def handle_buttons(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

        for button in self.buttons:
            button.render()
            clicked = button.update(mouse_pos, mouse_clicked)

            if clicked:
                if button.button_id == "ready_up_button":
                    self.player_ready = True

    def init_components(self):
        ready_up_button = Button(self.width - 200, 200, 200, 100, "READY", self.screen, "ready_up_button")
        self.buttons.append(ready_up_button)

    def add_player(self, player):
        self.players.append(player)
