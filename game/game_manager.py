from networking.network_simulator import NetworkSimulator
from game.client import Client
from client_scenes.main_menu import MainMenu
from rendering.splash_screen import SplashScreen
from client_scenes.lobby_scene import Lobby
from server_scenes.server_main_scene import ServerMainScene
from game.server import Server
from ui_components.join_lobby_window import JoinLobbyWindow


class GameManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.fake_net = NetworkSimulator()
        self.server = None
        self.client = None
        self.main_menu = MainMenu(screen)
        self.splash_screen = SplashScreen(self.screen, "../ui_art/splash.png")
        self.game_state = "splash"

    def run(self, dt, events):
        self.splash(dt)

        if self.game_state == "menu":
            self.main_menu.run(dt, events)
            if self.main_menu.game_state != "menu":
                self.game_state = self.main_menu.game_state
                self.handle_state_change()

        if self.client:
            self.client.run(dt, events)
            # Sync state up
            if self.client.state == "crash_back":
                self.client = None
                self.game_state = "menu"
                self.main_menu.game_state = "menu"
                return
            else:
                self.game_state = self.client.state

        if self.server:
            self.server.run(dt)

    def handle_state_change(self):
        if self.game_state == "single_player":
            self.client = Client(self.screen, self.clock, "single_player", True)
        elif self.game_state == "create_server":
            self.client = Client(self.screen, self.clock, "joining", True)
            self.server = Server()
            self.server.start()
            self.client.is_host = True
        elif self.game_state == "join_server":
            self.client = Client(self.screen, self.clock, "joining", False)

    def splash(self, dt):
        if self.game_state == "splash":
            self.splash_screen.update(dt)
            self.splash_screen.draw()
            if self.splash_screen.is_done():
                self.game_state = "menu"
