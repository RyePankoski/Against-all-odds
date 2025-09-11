from ui_components.join_lobby_window import JoinLobbyWindow
from networking.network_layer import NetworkLayer
from rendering.splash_screen import SplashScreen
from client_scenes.main_menu import MainMenu
from client_scenes.lobby_scene import Lobby
from game.client import Client
from game.server import Server

import pygame
import time
import json


class GameManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

        self.server = None
        self.main_menu = MainMenu(screen)
        self.splash_screen = SplashScreen(self.screen, "../resources/ui_art/splash.png")
        self.game_state = "splash"

        # Client-side components (created as needed)
        self.main_scene = None
        self.join_window = None
        self.lobby = None
        self.pause_menu = None
        self.is_host = False

        # Network state
        self.network_layer = None
        self.server_address = None
        self.waiting_for_server = False
        self.connection_attempt_time = None
        self.server_ip_address = None

        # Input tracking
        self.prev_inputs = None
        self.paused = False
        self.client = None

    def run(self, dt, events):
        self.splash(dt)
        self.run_menu(dt, events)

        if self.game_state == "single_player":
            self._run_single_player(dt, events)
        elif self.game_state == "joining":
            self.run_join_screen(dt, events)
        elif self.game_state == "lobby":
            self.lobby.run(events)

        if self.server:
            self.server.run(dt)

    def run_join_screen(self, dt, events):
        if self.waiting_for_server:
            self.await_server_confirmation()
            return

        self.join_window.run(dt, events)

        if self.join_window.number is not None and self.join_window.name is not None and not self.waiting_for_server:
            self.attempt_connection(self.join_window.number, self.join_window.name)

    def attempt_connection(self, server_ip, player_name):
        self.server_address = (server_ip, 4242)
        print(f"[CLIENT] Attempting connection to {self.server_address} as {player_name}")

        message = {
            "type": "CONNECTION_ATTEMPT",
            "player_name": player_name,
            "ready": False,
        }
        message = json.dumps(message).encode()
        self.network_layer.send_to(message, self.server_address)
        self.connection_attempt_time = time.time()

        self.waiting_for_server = True

    def await_server_confirmation(self):
        message = self.network_layer.listen_for_messages()
        if message is not None:
            data, address = message
            try:
                data = json.loads(data.decode())
                if data["type"] == "CONNECTION_CONFIRMATION":
                    server_message = data["message"]
                    print(f"[CLIENT] Connection successful, server says {server_message}")
                    self.game_state = "lobby"
            except json.decoder.JSONDecodeError:
                print("[CLIENT] Invalids message format, discarding.")

        if time.time() > self.connection_attempt_time + 60:
            print("[CLIENT] Connection timed out.")
            self.game_state = "menu"
            self.main_menu.game_state = "menu"

    def run_menu(self, dt, events):
        if self.game_state == "menu":
            self.main_menu.run(dt, events)
            if self.main_menu.game_state != "menu":
                self.game_state = self.main_menu.game_state
                self.handle_state_change()

    def _run_single_player(self, dt, events):
        self.client.run(dt, events)

    def setup_single_player(self):
        self.client = Client(self.screen, self.clock, False, None, None)
        pygame.mouse.set_visible(False)

    def setup_create_server(self):
        self.join_window = JoinLobbyWindow(self.screen)
        self.join_window.ip_box.set_text('127.0.0.1')

        # Create server-side network layer
        self.network_layer = NetworkLayer(bind_socket=True, port=4242)
        self.network_layer.start()
        self.server = Server(self.network_layer)

        # Create lobby for the host
        self.lobby = Lobby(self.screen, self.network_layer)
        self.is_host = True
        self.game_state = "joining"

    def setup_join_server(self):
        self.join_window = JoinLobbyWindow(self.screen)

        self.network_layer = NetworkLayer()
        self.network_layer.start()

        self.lobby = Lobby(self.screen, self.network_layer)
        self.is_host = False
        self.game_state = "joining"

    def handle_state_change(self):
        if self.game_state == "single_player":
            self.setup_single_player()
        elif self.game_state == "create_server":
            self.setup_create_server()
        elif self.game_state == "join_server":
            self.setup_join_server()

    def splash(self, dt):
        if self.game_state == "splash":
            self.splash_screen.update(dt)
            self.splash_screen.draw()
            if self.splash_screen.is_done():
                self.game_state = "menu"
