import json

from rendering.sprite_manager import SpriteManager
from ui_components.button import Button
from game.settings import *

import pygame


class Lobby:
    def __init__(self, screen, network_layer, server_ip):
        self.screen = screen
        self.network_layer = network_layer
        self.server_address = server_ip

        self.max_players = 10
        self.player_ready = False

        self.width, self.height = pygame.display.get_desktop_sizes()[0]
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.ship_sprite = SpriteManager.get_sprite("ship1")

        self.input_boxes = []
        self.buttons = []
        self.players = {}
        self.init_components()

        self.start_game = False

    def set_players(self, players):
        self.players = players

    def run(self, events):
        self.render()
        self.handle_buttons(events)
        self.listen_for_messages()

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
                    self.player_ready = not self.player_ready  # Toggle ready status
                    self.inform_server_ready()

    def inform_server_ready(self):
        if self.player_ready:
            message = {
                "type": "READY",
                "status": self.player_ready,
            }
            message = json.dumps(message).encode()
            print("[LOBBY] Player readied, sending to server]")
            self.network_layer.send_to(message, self.server_address)

    def listen_for_messages(self):
        message = self.network_layer.listen_for_messages()
        if message is not None:
            data, address = message
            try:
                data = json.loads(data.decode())
                print(f"[CLIENT LOBBY] Received message type: {data.get('type', 'UNKNOWN')}")
                
                if data["type"] == "PLAYERS_STATUS":
                    self.players = data["players"]
                elif data["type"] == "START_GAME":
                    print("[CLIENT] Server says to begin.")
                    if data.get("?", False):  # Server actually sends "?": True
                        print("[CLIENT] Setting start_game = True")
                        self.start_game = True
            except json.JSONDecodeError:
                print("[CLIENT] Invalid message format, discarding.")


    def render(self):
        # Title
        title_text = self.title_font.render("Waiting for Players...", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width / 2, 100))
        self.screen.blit(title_text, title_rect)

        # Player count
        count_text = self.font.render(f"Players: {len(self.players)}/{self.max_players}", True, (200, 200, 200))
        count_rect = count_text.get_rect(center=(self.width / 2, 140))
        self.screen.blit(count_text, count_rect)

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
                text_surf = self.font.render(player['name'], True, (255, 255, 255))
                self.screen.blit(text_surf, (list_x + 60, y_pos + 10))

                # Ready indicator - green if ready, red if not
                color = GREEN if player['ready'] else RED
                pygame.draw.circle(self.screen, color,
                                   (int(list_x + list_width - 20), int(y_pos + 20)), 5)
        else:
            # Show "No players connected" message
            no_players_text = self.font.render("No players connected", True, (150, 150, 150))
            no_players_rect = no_players_text.get_rect(center=(self.width / 2, 250))
            self.screen.blit(no_players_text, no_players_rect)

    def init_components(self):
        ready_up_button = Button(self.width - 200, 200, 200, 100, "READY", self.screen, "ready_up_button")
        self.buttons.append(ready_up_button)
