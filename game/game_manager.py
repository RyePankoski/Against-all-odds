from client_scenes.main_menu import MainMenu
from rendering.splash_screen import SplashScreen
from client_scenes.lobby_scene import Lobby
from client_scenes.main_scene import MainScene
from client_scenes.pause_menu import PauseMenu
from game.server import Server
from ui_components.join_lobby_window import JoinLobbyWindow
import socket
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
        self.sock = None
        self.server_address = None
        self.waiting_for_server = False
        self.connection_attempt_time = None
        self.server_ip_address = None

        # Input tracking
        self.prev_inputs = None
        self.paused = False

        # UI
        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)

    def run(self, dt, events):
        self.splash(dt)

        if self.game_state == "menu":
            self.main_menu.run(dt, events)
            if self.main_menu.game_state != "menu":
                self.game_state = self.main_menu.game_state
                self.handle_state_change()

        elif self.game_state == "single_player":
            self._run_single_player(dt, events)
        elif self.game_state == "joining":
            pygame.mouse.set_visible(True)
            result = self._run_joining(dt, events)
            if result == "connection_failed":
                self._cleanup_client_state()
                self.game_state = "menu"
                self.main_menu.game_state = "menu"
            elif result == "lobby":
                self.game_state = "lobby"

        elif self.game_state == "lobby":
            self._run_lobby(events)
        elif self.game_state == "in_game":
            self._run_multiplayer(events)

        if self.server:
            self.server.run(dt)

    def handle_state_change(self):
        if self.game_state == "single_player":
            self._setup_single_player()
        elif self.game_state == "create_server":
            self._setup_create_server()
        elif self.game_state == "join_server":
            self._setup_join_server()

    def _setup_single_player(self):
        self.main_scene = MainScene(self.screen, self.clock, False, 1)
        self.pause_menu = PauseMenu(self.screen, self.ui_font)
        pygame.mouse.set_visible(False)

    def _setup_create_server(self):
        self.join_window = JoinLobbyWindow(self.screen)
        self.lobby = Lobby(self.screen)
        self.join_window.ip_box.set_text('127.0.0.1')
        self.is_host = True
        self.server = Server()
        self.server.start()
        self.game_state = "joining"

    def _setup_join_server(self):
        self.join_window = JoinLobbyWindow(self.screen)
        self.lobby = Lobby(self.screen)
        self.is_host = False
        self.game_state = "joining"

    def _run_single_player(self, dt, events):
        # Handle global events
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.paused = not self.paused

        if self.paused:
            self.pause_menu.render()
            pygame.mouse.set_visible(True)
            return

        pygame.mouse.set_visible(False)
        inputs = self.collect_inputs()
        self.main_scene.inject_inputs(inputs)
        self.main_scene.run(dt)

    def _run_multiplayer(self, dt):
        # Send inputs
        input_data = self.collect_inputs()
        self.sock.sendto(json.dumps(input_data).encode(), self.server_address)

        # Receive game state
        try:
            data, addr = self.sock.recvfrom(1024)
            server_messages = [json.loads(data.decode())]
            self.main_scene.inject_server_data(server_messages, dt)
        except socket.error:
            pass

    def _run_joining(self, dt, events):
        self.join_window.run(dt, events)

        if self.join_window.number:
            self.server_ip = self.join_window.number

        if self.join_window.number and self.join_window.name and not self.waiting_for_server:
            self.connect(self.join_window.number, False, self.join_window.name)

        # Check for server response
        if self.waiting_for_server:
            return self.check_for_server_response()
        return None

    def _run_lobby(self, events):
        self.lobby.run(events)
        if self.lobby.player_ready:
            self.send_ready()
            if self.server.state == "in_game":
                self.game_state = "in_game"
        self.listen_for_server_updates()

    def send_ready(self):
        self.sock.sendto(json.dumps({"ready": True}).encode(), self.server_address)

    def connect(self, server_ip, ready, player_name="Anonymous"):
        self.server_address = (server_ip, 4242)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send JSON with connection info
        import json
        connection_data = {
            'type': 'connect',
            'player_name': player_name,
            'ready': ready,
        }

        message = json.dumps(connection_data).encode()
        self.sock.sendto(message, self.server_address)

        self.connection_attempt_time = time.time()
        self.waiting_for_server = True
        print(f"[CLIENT]Attempting to connect to {server_ip}:4242 as {player_name}...")

    def check_for_server_response(self):
        try:
            self.sock.settimeout(0)  # Non-blocking
            reply, server_addr = self.sock.recvfrom(1024)
            print(f"[CLIENT] Connected! Server said: {reply.decode()}")
            self.lobby.players.append((reply.decode()))
            self.server_address = server_addr
            self.waiting_for_server = False
            return "lobby"

        except socket.error:
            if time.time() - self.connection_attempt_time > 5.0:
                print("[CLIENT] Connection timeout - could not reach server")
                self.waiting_for_server = False
                return "connection_failed"

    def listen_for_server_updates(self):
        try:
            self.sock.settimeout(0)
            reply, server_addr = self.sock.recvfrom(1024)

            import json
            try:
                data = json.loads(reply.decode())
                if data.get('type') == 'player_list':
                    self.lobby.players = data['players']  # Update the lobby
                    print(f"[CLIENT] Lobby updated: {data['players']}")
            except json.JSONDecodeError:
                print(f"[CLIENT ]Server message: {reply.decode()}")
        except socket.error:
            pass

    def collect_inputs(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = self.main_scene.camera.screen_to_world(*mouse_screen_pos)

        # Get previous input state or initialize if first run
        prev_inputs = getattr(self, 'prev_inputs', {})

        input_package = {
            # Continuous inputs
            'w': keys[pygame.K_w],
            'a': keys[pygame.K_a],
            's': keys[pygame.K_s],
            'd': keys[pygame.K_d],
            'shift': keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
            'l': keys[pygame.K_l],
            'mouse_left': mouse_buttons[0],
            'mouse_world_pos': mouse_world_pos,
            "space": keys[pygame.K_SPACE],

            # Discrete inputs (just pressed)
            'r_pressed': keys[pygame.K_r] and not prev_inputs.get('r', False),
            't_pressed': keys[pygame.K_t] and not prev_inputs.get('t', False),
            '1_pressed': keys[pygame.K_1] and not prev_inputs.get('1', False),
            '2_pressed': keys[pygame.K_2] and not prev_inputs.get('2', False),
            'x_pressed': keys[pygame.K_x] and not prev_inputs.get('x', False),
            'alt_pressed': keys[pygame.K_LALT] and not prev_inputs.get('LAlt', False),

            'timestamp': time.time(),
        }

        # Store discrete keys for next frame comparison
        self.prev_inputs = {
            'r': keys[pygame.K_r],
            't': keys[pygame.K_t],
            '1': keys[pygame.K_1],
            '2': keys[pygame.K_2],
            'x': keys[pygame.K_x],
            'LAlt': keys[pygame.K_LALT],
        }

        return input_package

    def _cleanup_client_state(self):
        """Clean up client networking state"""
        if self.sock:
            self.sock.close()
            self.sock = None
        self.server_address = None
        self.waiting_for_server = False
        self.connection_attempt_time = None

    def splash(self, dt):
        if self.game_state == "splash":
            self.splash_screen.update(dt)
            self.splash_screen.draw()
            if self.splash_screen.is_done():
                self.game_state = "menu"
