from client_scenes.main_scene import MainScene
from client_scenes.pause_menu import PauseMenu
import pygame
import time


class Client:
    def __init__(self, screen, clock, fake_net, connected):
        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)
        self.connected = connected
        self.pause_menu = PauseMenu(screen, self.ui_font)
        self.fake_net = fake_net

        self.scenes = {"main_scene": MainScene(screen, clock, connected, 1)}
        self.scene = None

        self.scene = self.scenes["main_scene"]

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

        input_package = {
            # Movement keys
            'w': keys[pygame.K_w],
            'a': keys[pygame.K_a],
            's': keys[pygame.K_s],
            'd': keys[pygame.K_d],

            # Action keys
            'space': keys[pygame.K_SPACE],  # brake
            'shift': keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],  # boost
            'r': keys[pygame.K_r],  # radar pulse

            # Control panel keys
            'x': keys[pygame.K_x],  # toggle dampening
            'l': keys[pygame.K_l],  # continuous radar

            # Weapon selection
            '1': keys[pygame.K_1],  # missile
            '2': keys[pygame.K_2],  # bullet

            # Mouse input
            'mouse_left': mouse_buttons[0],  # fire weapon
            'mouse_world_pos': mouse_world_pos,  # for aiming

            # Timestamp for lag compensation
            'timestamp': time.time()
        }

        return input_package
