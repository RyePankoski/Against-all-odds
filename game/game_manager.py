from networking.network_simulator import NetworkSimulator
from game.server import Server
from game.client import Client
from client_scenes.main_menu import MainMenu
from client_scenes.lobby_scene import Lobby
from rendering.splash_screen import SplashScreen


class GameManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

        self.fake_net = NetworkSimulator()

        self.server = None
        self.client = None
        self.main_menu = MainMenu(screen)
        self.lobby = Lobby()
        self.splash_screen = SplashScreen(self.screen, "../ui_art/splash.png")
        self.game_state = "splash"

    def run(self, dt, events):
        if self.game_state == "splash":
            self.splash_screen.update(dt)
            self.splash_screen.draw()
            if self.splash_screen.is_done():
                self.game_state = "menu"

        if self.game_state == "menu":
            self.main_menu.run(dt, events)
            if self.main_menu.game_state != "menu":
                self.game_state = self.main_menu.game_state
                self.handle_state_change()

        elif self.game_state == "single_player":
            self.client.run(dt, events)
        elif self.game_state == "multiplayer":
            self.client.run(dt, events)
            self.server.run(dt)

    def handle_state_change(self):
        if self.game_state == "single_player":
            self.client = Client(self.screen, self.clock, False, self.fake_net)
        elif self.game_state == "multiplayer":
            self.server = Server(self.fake_net)
            self.client = Client(self.screen, self.clock, True, self.fake_net)
