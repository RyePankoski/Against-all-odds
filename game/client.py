from scenes.main_scene import MainScene
from scenes.pause_menu import PauseMenu
import pygame
import time


class Client:
    def __init__(self, screen, clock, fake_net, connected):
        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)
        self.connected = connected
        self.main_scene = MainScene(screen, clock, connected, 1)
        self.pause_menu = PauseMenu(screen, self.ui_font)
        self.fake_net = fake_net

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
        self.main_scene.inject_inputs(inputs)
        self.main_scene.run(dt)

        if self.connected:
            self.send_data_to_server(inputs)
            self.get_data_from_server()

    def send_data_to_server(self, inputs):
        if len(inputs) > 0:
            pass

        if inputs:
            message = {
                'player_id': self.main_scene.player_number,
                'input_data': inputs,
                'timestamp': time.time()
            }
            self.fake_net.send_to_server(message)

    def get_data_from_server(self):
        server_messages = self.fake_net.get_client_messages()

        if len(server_messages) > 0:
            pass

        for message in server_messages:
            self.main_scene.all_ships = message.get('ships', self.main_scene.all_ships)
            self.main_scene.all_missiles = message.get('missiles', self.main_scene.all_missiles)
            self.main_scene.all_bullets = message.get('bullets', self.main_scene.all_bullets)
            self.main_scene.all_asteroids = message.get('asteroids', self.main_scene.all_asteroids)
            self.main_scene.explosion_events.extend(message.get('explosions', []))

            ships = message.get('ships', [])

            for ship in ships:
                if ship.owner == self.main_scene.player_number:
                    self.main_scene.ship.x = ship.x
                    self.main_scene.ship.y = ship.y
                    break

    def collect_inputs(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = self.main_scene.camera.screen_to_world(*mouse_screen_pos)

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
