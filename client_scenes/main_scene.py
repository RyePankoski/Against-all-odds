import random
from rendering.render_util import *
from rendering.camera import Camera
from entities.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from ship_subsystems.radar_system import RadarSystem
from game.ai import AI
from client_scenes.victory_screen import VictoryScreen
from client_scenes.defeat_screen import DefeatScreen


class MainScene:
    def __init__(self, screen, clock, connected, player_number):
        self.screen = screen
        self.clock = clock
        self.connected = connected
        self.player_number = player_number

        # Game state
        self.victory = False
        self.game_over = False
        self.inputs = []

        # Game objects
        self.all_bullets = []
        self.all_missiles = []
        self.all_asteroids = {}
        self.all_ships = []
        self.all_ai = []
        self.radar_signatures = []
        self.explosion_events = []

        # Rendering
        self.star_tiles = generate_star_tiles()
        self.camera = Camera(self.screen)
        self.ui_font = pygame.font.SysFont('microsoftyahei', 20)

        # Game systems
        self.radar_system = RadarSystem()
        self.victory_screen = VictoryScreen(self.screen)
        self.defeat_screen = DefeatScreen()

        # AI configuration
        self.number_of_ai = 1

        # Initialize game
        self.setup_game()

    def setup_game(self):
        """Initialize the game world and entities"""
        # Create player ship
        self.ship = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, self.player_number, self.camera)
        self.all_ships.append(self.ship)

        # Create AI ships if in single player
        self.spawn_ai_ships()

    def spawn_ai_ships(self):
        """Create AI ships for single player mode"""
        if not self.connected:
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

    def run(self, dt):
        """Main game loop - handles all game updates and rendering"""
        self.update_ai(dt)
        self.check_game_state()

        if self.ship:
            self.update_player_ship(dt)

        if not self.connected:
            self.update_game_objects()

        self.render()
        self.handle_victory_screen()

    def update_ai(self, dt):
        """Update AI and remove dead ones"""
        for ai in self.all_ai[:]:  # Copy list to avoid modification during iteration
            ai.run(dt)
            if not ai.ship.alive:
                self.all_ai.remove(ai)

    def check_game_state(self):
        """Check win/lose conditions"""
        if len(self.all_ai) <= 0:
            self.victory = True

        if self.ship and self.ship.health <= 0:
            self.ship = None
            self.game_over = True

    def update_player_ship(self, dt):
        """Update player ship and handle radar"""
        self.ship.update(dt)
        apply_inputs_to_ship(self.ship, self.inputs)
        self.camera.follow_target(self.ship.x, self.ship.y)

        # Handle radar pulse
        if self.ship.wants_radar_pulse and self.ship.power > 20:
            self.ship.power *= (1 - (self.ship.radar_resolution / MAX_RADAR_RESOLUTION)) - 0.2
            self.ship.power = max(0, self.ship.power)

            self.radar_signatures.clear()
            self.radar_system.begin_scan(self.ship, self.all_ships, self.all_asteroids)
            self.ship.can_pulse = False
            self.ship.wants_radar_pulse = False

        # Continue radar scanning
        if self.radar_system.scanning:
            self.radar_signatures.extend(self.radar_system.continue_scan())

    def update_game_objects(self):
        """Update all game objects and handle collisions"""
        # Handle collisions and physics
        if self.ship:
            check_ship_collisions(self.ship, self.all_asteroids)

        handle_asteroids(self.all_asteroids)

        # Collect projectiles from ships
        self.collect_projectiles()

        # Update projectiles
        self.update_projectiles()

        # Remove dead ships
        self.remove_dead_ships()

    def collect_projectiles(self):
        """Collect projectiles from all ships"""
        for ship in self.all_ships:
            self.all_bullets.extend(ship.bullets)
            self.all_missiles.extend(ship.missiles)
            ship.bullets.clear()
            ship.missiles.clear()

    def update_projectiles(self):
        """Update all projectiles and handle collisions"""
        handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
        handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events)

    def remove_dead_ships(self):
        """Remove ships that are no longer alive"""
        for ship in self.all_ships[:]:
            if not ship.alive:
                self.all_ships.remove(ship)

    def handle_victory_screen(self):
        """Handle victory screen logic"""
        if self.victory:
            self.victory_screen.run()
            if self.victory_screen.state_to_extract == "new_game":
                self.reset_game()

    def reset_game(self):
        """Reset game state for new game"""
        # Clear all game objects
        self.all_bullets.clear()
        self.all_missiles.clear()
        self.all_asteroids.clear()
        self.all_ships.clear()
        self.all_ai.clear()
        self.radar_signatures.clear()
        self.explosion_events.clear()

        # Reset game state
        self.victory = False
        self.game_over = False

        # Restart the game
        self.setup_game()

    def render(self):
        """Render all game elements"""
        draw_stars_tiled(self.star_tiles, self.camera, self.screen,
                         self.camera.screen_width, self.camera.screen_width)
        draw_ships(self.all_ships, self.camera, self.screen)
        draw_missiles(self.all_missiles, self.camera, self.screen)
        draw_bullets(self.all_bullets, self.camera, self.screen)
        draw_asteroids(self.all_asteroids, self.camera, self.screen, WORLD_WIDTH, WORLD_HEIGHT)

        draw_explosions(self.screen, self.explosion_events, self.camera)
        self.explosion_events.clear()

        if self.all_ships:  # Make sure we have ships before accessing index 0
            draw_radar_screen(self.screen, self.radar_signatures,
                              (self.all_ships[0].x, self.all_ships[0].y), self.all_missiles)

        draw_ship_data(self.screen, self.ship, self.ui_font)
        draw_fps(self.screen, self.clock, self.ui_font)

    def inject_inputs(self, inputs):
        """Receive input data from client"""
        self.inputs = inputs

    def inject_server_data(self, server_messages):
        """Handle multiplayer server data"""
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
        """Interpolate player ship position for multiplayer"""
        x_diff = abs(ship.x - self.ship.x)
        y_diff = abs(ship.y - self.ship.y)

        x_interpolate = x_diff / 2
        y_interpolate = y_diff / 2

        if ship.x > self.ship.x:
            self.ship.x += x_interpolate
        elif ship.x < self.ship.x:
            self.ship.x -= x_interpolate

        if ship.y > self.ship.y:
            self.ship.y += y_interpolate
        elif ship.y < self.ship.y:
            self.ship.y -= y_interpolate

        self.ship.dx = ship.dx
        self.ship.dy = ship.dy
