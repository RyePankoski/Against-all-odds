from client_scenes.main_scene import MainScene
from client_scenes.pause_menu import PauseMenu

import pygame
import json
import time


class Client:
    def __init__(self, screen, clock, connected, network_layer, server_address, client_address):
        self.prev_inputs = None
        self.connected = connected
        self.network_layer = network_layer
        self.server_address = server_address
        self.main_scene = MainScene(screen, clock, connected, client_address)
        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)
        self.pause_menu = PauseMenu(screen, self.ui_font)
        self.server_data = None
        self.paused = False

    def run(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.paused = not self.paused

        if self.paused:
            self.pause_menu.render()
            pygame.mouse.set_visible(True)
            return
        else:
            pygame.mouse.set_visible(False)

        inputs = self.collect_inputs()

        self.main_scene.inject_inputs(inputs)
        self.main_scene.run(dt)

        if self.connected:
            self.send_inputs_to_server(inputs)
            self.listen_for_server_data(dt)

    def listen_for_server_data(self, dt):
        message = self.network_layer.listen_for_messages()

        if message is not None:
            data, address = message
            try:
                message = json.loads(data.decode())

                if message['type'] == "GAME_UPDATE":
                    self.main_scene.inject_server_data(data, dt)
                else:
                    pass
            except json.decoder.JSONDecodeError:
                print("[CLIENT] Invalids message format, discarding.")

    def send_inputs_to_server(self, inputs=None):
        if inputs and self.server_address:
            message = json.dumps(inputs).encode()
            self.network_layer.send_to(message, self.server_address)

    def collect_inputs(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = self.main_scene.camera.screen_to_world(*mouse_screen_pos)

        # Get previous input state or initialize if first run
        prev_inputs = getattr(self, 'prev_inputs', {})

        input_package = {
            "type": "PLAYER_INPUT",
            "input_data": {  # Changed from "data" to "input_data" to match server
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
            },
            "timestamp": time.time(),
        }

        # Store current inputs for next frame comparison
        self.prev_inputs = {
            'r': keys[pygame.K_r],
            't': keys[pygame.K_t],
            '1': keys[pygame.K_1],
            '2': keys[pygame.K_2],
            'x': keys[pygame.K_x],
            'LAlt': keys[pygame.K_LALT],
        }

        return input_package
