from ui_components.join_lobby_window import JoinLobbyWindow
from client_scenes.main_scene import MainScene
from client_scenes.pause_menu import PauseMenu
from client_scenes.lobby_scene import Lobby
import socket
import pygame
import time

class Client:
    def __init__(self, screen, clock, state, host):
        self.state = state
        self.main_scene = None
        self.is_host = host

        if state == "single_player":
            self.main_scene = MainScene(screen, clock, state, 1)

        self.join_window = JoinLobbyWindow(screen)
        self.lobby = Lobby(screen)

        if self.is_host:
            self.join_window.ip_box.set_text('127.0.0.1')

        self.prev_inputs = None
        self.paused = False

        pygame.mouse.set_visible(False)
        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)
        self.pause_menu = PauseMenu(screen, self.ui_font)

        self.sock = None
        self.server_address = None
        self.waiting_for_server = False
        self.connection_attempt_time = None

    def run(self, dt, events):
        # Handle global events
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.paused = not self.paused

        if self.state == "single_player":
            self._run_single_player(dt)
        elif self.state == "joining":
            pygame.mouse.set_visible(True)
            self._run_joining(dt, events)
        elif self.state == "multiplayer_in_game":
            self._run_multiplayer(dt)
        elif self.state == "lobby":
            self._run_lobby(dt, events)

    def _run_lobby(self, dt, events):
        self.lobby.run()
        self.listen_for_server_updates()

    def listen_for_server_updates(self):
        try:
            self.sock.settimeout(0)
            reply, server_addr = self.sock.recvfrom(1024)

            import json
            try:
                data = json.loads(reply.decode())
                if data.get('type') == 'player_list':
                    self.lobby.players = data['players']  # Update the lobby
                    print(f"Lobby updated: {data['players']}")
            except json.JSONDecodeError:
                print(f"Server message: {reply.decode()}")
        except socket.error:
            pass

    def _run_joining(self, dt, events):
        self.join_window.run(dt, events)

        if self.join_window.number and self.join_window.name and not self.waiting_for_server:
            self.connect(self.join_window.number, self.join_window.name)

        # Check for server response
        if self.waiting_for_server:
            self.check_for_server_response()

    def _run_single_player(self, dt):
        if self.paused:
            self.pause_menu.render()
            pygame.mouse.set_visible(True)
            return

        inputs = self.collect_inputs()
        self.main_scene.inject_inputs(inputs)
        self.main_scene.run(dt)

    def _run_multiplayer(self, dt):
        pass

    def connect(self, server_ip, player_name="Anonymous"):
        print(f"Connecting to: '{server_ip}' as '{player_name}'")
        self.server_address = (server_ip, 4242)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send JSON with connection info
        import json
        connection_data = {
            'type': 'connect',
            'player_name': player_name
        }
        message = json.dumps(connection_data).encode()
        self.sock.sendto(message, self.server_address)

        self.connection_attempt_time = time.time()
        self.waiting_for_server = True
        print(f"Attempting to connect to {server_ip}:4242 as {player_name}...")

    def check_for_server_response(self):
        try:
            self.sock.settimeout(0)  # Non-blocking
            reply, server_addr = self.sock.recvfrom(1024)
            print(f"Connected! Server said: {reply.decode()}")
            self.lobby.players.append(reply.decode())
            self.state = "lobby"
            self.waiting_for_server = False

        except socket.error:
            if time.time() - self.connection_attempt_time > 5.0:
                print("Connection timeout - could not reach server")
                self.waiting_for_server = False
                self.state = "crash_back"

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
