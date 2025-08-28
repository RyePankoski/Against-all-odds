from shared_util.radar_logic import radar_pulse
from rendering.render_util import *
from rendering.camera import Camera
from entities.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
import time


class Client:
    def __init__(self, player_number, is_local_player, screen, clock, fake_net, connected, simulation):
        self.fake_network = fake_net
        self.player_number = player_number
        self.is_local_player = is_local_player
        self.screen = screen
        self.clock = clock
        self.connected = connected
        self.simulation = simulation

        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT

        self.username = ""
        self.password = ""

        self.last_active = 0
        self.address = None
        self.port = None

        self.score = 0
        self.kills = 0
        self.deaths = 0

        self.is_admin = False
        self.in_lobby = True
        self.ready = False

        self.color = (255, 255, 255)
        self.input_sequence = 0
        self.last_processed_input = 0
        self.latency = 0
        self.cheat_warnings = 0
        self.cheat_detected = False

        self.all_bullets = []
        self.all_missiles = []
        self.all_asteroids = {}
        self.all_ships = []
        self.radar_signatures = []
        self.explosion_events = []

        self.star_tiles = generate_star_tiles()

        self.camera = Camera(self.screen)
        self.ship = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, self.player_number, self.camera)
        self.all_ships.append(self.ship)

        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)

        if not self.connected:
            self.all_asteroids = generate_some_asteroids()

    def run(self, dt):

        if self.connected:
            if self.simulation is True:
                self.handle_ship(dt)
                self.collect_bullets(self.ship)
                self.collect_missiles(self.ship)
                handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
                handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events)
                apply_inputs_to_ship(self.ship, self.collect_inputs())
            self.send_data_to_server()
            self.get_data_from_server()
        else:
            handle_asteroids(self.all_asteroids)

            self.handle_ship(dt)
            self.collect_bullets(self.ship)
            self.collect_missiles(self.ship)
            handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
            handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events)
            apply_inputs_to_ship(self.ship, self.collect_inputs())
            self.send_data_to_server()
            self.get_data_from_server()

        if self.is_local_player:
            self.camera.follow_target(self.ship.x, self.ship.y)
            self.render()

    def handle_ship(self, dt):
        self.ship.update(dt)
        check_ship_collisions(self.ship, self.all_asteroids)
        if self.ship.wants_radar_pulse:
            signatures = radar_pulse(self.all_ships, self.all_asteroids, self.ship)
            self.set_radar_signatures(signatures)
            self.ship.wants_radar_pulse = False

    def send_data_to_server(self):
        inputs = self.collect_inputs()

        if len(inputs) > 0:
            pass

        if inputs:
            message = {
                'player_id': self.player_number,
                'input_data': inputs,
                'timestamp': time.time()
            }
            self.fake_network.send_to_server(message)

    def get_data_from_server(self):
        server_messages = self.fake_network.get_client_messages()

        if len(server_messages) > 0:
            pass

        for message in server_messages:
            self.all_ships = message.get('ships', self.all_ships)
            self.all_missiles = message.get('missiles', self.all_missiles)
            self.all_bullets = message.get('bullets', self.all_bullets)
            self.all_asteroids = message.get('asteroids', self.all_asteroids)
            self.explosion_events.extend(message.get('explosions', []))

            # Update ship reference
            for ship in self.all_ships:
                if ship.owner == self.player_number:
                    self.ship = ship
                    break

    def collect_inputs(self):
        if self.is_local_player:
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_screen_pos = pygame.mouse.get_pos()
            mouse_world_pos = self.camera.screen_to_world(*mouse_screen_pos)

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

        return None

    def render(self):
        draw_stars_tiled(self.star_tiles, self.camera, self.screen, self.camera.screen_width, self.camera.screen_height)
        draw_ships(self.all_ships, self.camera, self.screen)
        draw_missiles(self.all_missiles, self.camera, self.screen)
        draw_bullets(self.all_bullets, self.camera, self.screen)
        draw_asteroids(self.all_asteroids, self.camera, self.screen, WORLD_WIDTH, WORLD_HEIGHT)

        draw_explosions(self.screen, self.explosion_events, self.camera)
        self.explosion_events.clear()

        draw_radar_screen(self.screen, self.radar_signatures,
                          (self.all_ships[0].x, self.all_ships[0].y), self.all_missiles)
        draw_ship_data(self.screen, self.ship, self.ui_font)
        draw_fps(self.screen, self.clock, self.ui_font)

    def set_radar_signatures(self, signatures):
        self.radar_signatures = signatures

    def init_star_field(self):
        star_field = []

        for x in range(0, self.world_width, 50):
            for y in range(0, self.world_height, 50):
                if random.random() < 0.005:
                    star_field.append((x, y, random.uniform(0.5, 7)))

        return star_field

    def collect_missiles(self, ship):
        new_missiles = ship.missiles
        self.all_missiles.extend(new_missiles)
        ship.missiles.clear()

    def collect_bullets(self, ship):
        new_bullets = ship.bullets
        self.all_bullets.extend(new_bullets)
        ship.bullets.clear()
