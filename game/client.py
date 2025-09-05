from client_scenes.main_scene import MainScene
from client_scenes.pause_menu import PauseMenu

import pygame
import time


class Client:
    def __init__(self, screen, clock, connected, fake_net):
        self.connected = connected
        self.fake_net = fake_net

        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)

        self.scenes = {"main_scene": MainScene(screen, clock, connected, 1)}
        self.scene = self.scenes["main_scene"]
        self.pause_menu = PauseMenu(screen, self.ui_font)

        self.prev_inputs = None
        self.paused = False

    def run(self, dt, events):
        inputs = self.collect_inputs()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

        if self.paused:
            self.pause_menu.render()
        else:
            self.run_scene(inputs, dt)

    def run_scene(self, inputs, dt):

        if self.connected:
            self.send_data_to_server(inputs)
            self.get_data_from_server()

        self.scene.inject_inputs(inputs)
        self.scene.run(dt)

    def send_data_to_server(self, inputs):
        if len(inputs) > 0:
            pass

        if inputs:
            message = {
                'player_id': self.scene.player_number,
                'input_data': inputs,
                'timestamp': time.time()
            }
            self.fake_net.send_to_server(message)

    def get_data_from_server(self):
        self.scene.inject_server_data(self.fake_net.get_client_messages())

    def collect_inputs(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = self.scene.camera.screen_to_world(*mouse_screen_pos)

        # Get previous input state or initialize if first run
        prev_inputs = getattr(self, 'prev_inputs', {})

        input_package = {
            # Continuous inputs
            'w': keys[pygame.K_w],
            'a': keys[pygame.K_a],
            's': keys[pygame.K_s],
            'd': keys[pygame.K_d],
            'space': keys[pygame.K_SPACE],
            'shift': keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
            'l': keys[pygame.K_l],
            'mouse_left': mouse_buttons[0],
            'mouse_world_pos': mouse_world_pos,

            # Discrete inputs (just pressed)
            'r_pressed': keys[pygame.K_r] and not prev_inputs.get('r', False),
            't_pressed': keys[pygame.K_t] and not prev_inputs.get('t', False),
            '1_pressed': keys[pygame.K_1] and not prev_inputs.get('1', False),
            '2_pressed': keys[pygame.K_2] and not prev_inputs.get('2', False),
            'x_pressed': keys[pygame.K_x] and not prev_inputs.get('x', False),

            'timestamp': time.time()
        }

        # Store discrete keys for next frame comparison
        self.prev_inputs = {
            'r': keys[pygame.K_r],
            't': keys[pygame.K_t],
            '1': keys[pygame.K_1],
            '2': keys[pygame.K_2],
            'x': keys[pygame.K_x]
        }

        return input_package
