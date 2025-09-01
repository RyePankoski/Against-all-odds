from shared_util.radar_logic import radar_pulse
from rendering.render_util import *
from rendering.camera import Camera
from entities.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *


class MainScene:
    def __init__(self, screen, clock, connected, player_number):
        self.screen = screen
        self.clock = clock
        self.connected = connected
        self.player_number = player_number

        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT

        self.username = ""
        self.password = ""

        self.last_active = 0
        self.address = None
        self.port = None
        self.inputs = []

        self.score = 0
        self.kills = 0
        self.deaths = 0

        self.is_admin = False
        self.in_lobby = True
        self.ready = False

        self.player_number = 1

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

        self.tile_size = 1024
        self.star_tiles = generate_star_tiles()

        self.camera = Camera(self.screen)
        self.ship = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, self.player_number, self.camera)
        self.all_ships.append(self.ship)

        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)

        if not self.connected:
            self.all_asteroids = generate_some_asteroids()

    def run(self, dt):
        # Update game objects
        if self.ship:
            self.ship.update(dt)
            apply_inputs_to_ship(self.ship, self.inputs)
            check_ship_collisions(self.ship, self.all_asteroids)

            # Radar
            if self.ship.wants_radar_pulse:
                self.radar_signatures = radar_pulse(self.all_ships, self.all_asteroids, self.ship)
                self.ship.can_pulse = False
                self.ship.wants_radar_pulse = False

            # Collect projectiles
            self.all_bullets.extend(self.ship.bullets)
            self.all_missiles.extend(self.ship.missiles)
            self.ship.bullets.clear()
            self.ship.missiles.clear()

            if self.ship.health <= 0:
                self.ship = None

        if not self.connected:
            handle_asteroids(self.all_asteroids)
            handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
            handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events)

        if self.ship:
            self.camera.follow_target(self.ship.x, self.ship.y)
        self.render()

    def render(self):
        draw_stars_tiled(self.star_tiles, self.camera, self.screen,
                         self.camera.screen_width, self.camera.screen_width)
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

    def collect_missiles(self, ship):
        new_missiles = ship.missiles
        self.all_missiles.extend(new_missiles)
        ship.missiles.clear()

    def collect_bullets(self, ship):
        new_bullets = ship.bullets
        self.all_bullets.extend(new_bullets)
        ship.bullets.clear()

    def inject_inputs(self, inputs):
        self.inputs = inputs


