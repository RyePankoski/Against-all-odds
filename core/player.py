from rendering.render_util import *
from rendering.camera import Camera
from entities.ship import Ship


class Player:
    def __init__(self, player_number, is_local_player, screen, clock):
        self.player_number = player_number
        self.is_local_player = is_local_player
        self.screen = screen
        self.clock = clock

        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT

        self.username = ""
        self.password = ""
        self.connected = True
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
        self.star_field = []
        self.radar_signatures = []
        self.explosion_events = []

        self.camera = Camera(self.screen)
        self.ship = Ship(WORLD_WIDTH/2, WORLD_HEIGHT/2, self.player_number, self.camera)

    def run(self):
        self.handle_inputs()
        self.handle_ship()

        if self.is_local_player:
            self.camera.follow_target(self.ship.x, self.ship.y)
            self.render()

    def handle_ship(self):
        self.ship.update()
        self.ship.check_for_collisions(self.all_asteroids)

    def handle_inputs(self):
        if self.is_local_player:
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            self.ship.handle_ship_inputs(keys, mouse_buttons)

    def inject_data(self, game_state):
        self.all_missiles = game_state[0]
        self.all_bullets = game_state[1]
        self.all_ships = game_state[2]
        self.all_asteroids = game_state[3]
        self.star_field = game_state[4]
        self.radar_signatures = game_state[5]
        self.explosion_events = game_state[6]

    def render(self):
        draw_ships(self.all_ships, self.camera, self.screen)
        draw_stars(self.star_field, self.camera, self.screen, WORLD_WIDTH, WORLD_HEIGHT)
        draw_missiles(self.all_missiles, self.camera, self.screen)
        draw_bullets(self.all_bullets, self.camera, self.screen)
        draw_asteroids(self.all_asteroids, self.camera, self.screen, WORLD_WIDTH, WORLD_HEIGHT)

        draw_explosions(self.screen, self.explosion_events, self.camera)

        draw_radar_screen(self.screen, self.radar_signatures,
                          (self.all_ships[0].x, self.all_ships[0].y), self.all_missiles)
        draw_ship_data(self.screen, self.ship)
        draw_fps(self.screen, self.clock)
