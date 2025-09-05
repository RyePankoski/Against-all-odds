import random

from rendering.render_util import *
from rendering.camera import Camera
from entities.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from ship_subsystems.radar_system import RadarSystem
from game.ai import AI


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

        self.number_of_ai = 50
        self.all_ai = []

        self.ship = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, self.player_number, self.camera)
        self.all_ships.append(self.ship)

        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)
        self.radar_system = RadarSystem()

        if not self.connected:
            # self.all_asteroids = generate_some_asteroids()
            for _ in range(self.number_of_ai):
                ai_ship = Ship(
                    random.randint(0, WORLD_WIDTH),
                    random.randint(0, WORLD_HEIGHT),
                    -1,
                    None
                )
                self.all_ships.append(ai_ship)
                ai = AI(ai_ship, self.ship, self.all_ships, self.all_asteroids)
                self.all_ai.append(ai)

        else:
            self.ai = None

    def run(self, dt):

        if len(self.all_ai) > 0:
            for ai in self.all_ai:
                ai.run(dt)

        if self.ship:

            self.ship.update(dt)
            apply_inputs_to_ship(self.ship, self.inputs)
            self.camera.follow_target(self.ship.x, self.ship.y)

            # Radar
            if self.ship.wants_radar_pulse and self.ship.power > 20:
                self.ship.power *= (1 - (self.ship.radar_resolution / MAX_RADAR_RESOLUTION)) - 0.2
                self.ship.power = (max(0, self.ship.power))

                self.radar_signatures.clear()
                self.radar_system.begin_scan(self.ship, self.all_ships, self.all_asteroids)
                self.ship.can_pulse = False
                self.ship.wants_radar_pulse = False

            if self.radar_system.scanning:
                self.radar_signatures.extend(self.radar_system.continue_scan())

            if self.ship.health <= 0:
                self.ship = None

        if not self.connected:
            check_ship_collisions(self.ship, self.all_asteroids)
            handle_asteroids(self.all_asteroids)
            handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
            handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events)

            for ship in self.all_ships:
                self.all_bullets.extend(ship.bullets)
                self.all_missiles.extend(ship.missiles)
                ship.bullets.clear()
                ship.missiles.clear()

                if ship.alive is False:
                    self.all_ships.remove(ship)

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

    def inject_server_data(self, server_messages):
        for message in server_messages:
            self.all_ships = message.get('ships', self.all_ships)
            self.all_missiles = message.get('missiles', self.all_missiles)
            self.all_bullets = message.get('bullets', self.all_bullets)
            self.all_asteroids = message.get('asteroids', self.all_asteroids)
            self.explosion_events.extend(message.get('explosions', []))

            ships = message.get('ships', [])

            for ship in ships:
                if ship.owner == self.player_number:
                    self.ship.shield = ship.shield
                    self.ship.health = ship.health

                    self.interpolate(ship)
                    break

    def interpolate(self, ship):
        xDiff = abs(ship.x - self.ship.x)
        yDiff = abs(ship.y - self.ship.y)

        xInterpolate = xDiff / 2
        yInterpolate = yDiff / 2

        if ship.x > self.ship.x:
            self.ship.x += xInterpolate
        elif ship.x < self.ship.x:
            self.ship.x -= xInterpolate
        if ship.y > self.ship.y:
            self.ship.y += yInterpolate
        elif ship.y < self.ship.y:
            self.ship.y -= yInterpolate

        self.ship.dx = ship.dx
        self.ship.dy = ship.dy
