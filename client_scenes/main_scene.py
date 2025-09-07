from rendering.camera import Camera
from entities.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from ship_subsystems.radar_system import RadarSystem
from game.ai import AI
from client_scenes.victory_screen import VictoryScreen
from client_scenes.defeat_screen import DefeatScreen
from rendering.world_render import WorldRender


class MainScene:
    def __init__(self, screen, clock, connected, player_number):
        self.ship = None
        self.screen = screen
        self.clock = clock
        self.connected = connected
        self.player_number = player_number

        # Game state
        self.victory = False
        self.defeat = False
        self.inputs = []

        # Game objects
        self.all_bullets = []
        self.all_rockets = []
        self.all_asteroids = {}
        self.all_ships = []
        self.all_ai = []
        self.radar_signatures = []
        self.explosion_events = []

        # Network elements
        self.frame = 0
        self.server_saw_collision = False

        # Rendering
        self.camera = Camera(self.screen)

        # Game systems
        self.radar_system = RadarSystem()

        # UI components
        self.victory_screen = VictoryScreen(self.screen)
        self.defeat_screen = DefeatScreen(self.screen)
        self.world_render = WorldRender(self.screen)

        # AI configuration
        self.number_of_ai = 1
        self.ai_difficulty = 2

        # Initialize game
        self.setup_game()

    def setup_game(self):
        """Initialize the game world and entities"""
        # Create player ship
        self.ship = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, self.player_number, self.camera)
        self.all_ships.append(self.ship)

        if not self.connected:
            self.all_asteroids = generate_some_asteroids()

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
                ai = AI(ai_ship, self.ship, self.all_ships, self.all_asteroids, self.ai_difficulty)
                self.all_ai.append(ai)

    def run(self, dt):
        """Main game loop - handles all game updates and rendering"""
        self.frame += 1
        self.update_ai(dt)
        self.check_game_state()

        if self.ship:
            self.update_player_ship(dt)

        if not self.connected:
            self.update_game_objects()

        self.render()
        self.handle_victory_screen()
        self.handle_defeat_screen()

    def update_ai(self, dt):
        """Update AI and remove dead ones"""
        for ai in self.all_ai[:]:  # Copy list to avoid modification during iteration
            ai.run(dt)
            if not ai.ship.alive:
                self.all_ai.remove(ai)

    def check_game_state(self):
        """Check win/lose conditions"""
        if len(self.all_ai) <= 0 and not self.connected:
            self.victory = True

        if self.ship and self.ship.health <= 0:
            self.ship = None
            self.defeat = True

    def update_player_ship(self, dt):
        """Update player ship and handle radar"""
        self.ship.update(dt)
        apply_inputs_to_ship(self.ship, self.inputs)

        # Handle radar pulse
        if self.ship.is_radar_on:
            if self.ship.can_radar_pulse is True:
                print("start pulse")
                self.radar_signatures.clear()
                self.radar_system.begin_scan(self.ship, self.all_ships, self.all_asteroids)
                self.ship.can_radar_pulse = False
                self.ship.enemy_radar_ping_coordinates.clear()

        if self.radar_system.scanning:
            print("pulsing")
            self.radar_signatures.extend(self.radar_system.continue_scan())

    def update_game_objects(self):
        """Update all game objects and handle collisions"""
        # Handle collisions and physics

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
            self.all_rockets.extend(ship.rockets)
            ship.bullets.clear()
            ship.rockets.clear()

    def update_projectiles(self):
        """Update all projectiles and handle collisions"""
        handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
        handle_rockets(self.all_rockets, self.all_ships, self.all_asteroids, self.explosion_events)

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

    def handle_defeat_screen(self):
        if self.defeat:
            self.defeat_screen.run()
            if self.defeat_screen.state_to_extract == "new_game":
                self.reset_game()

    def reset_game(self):
        """Reset game state for new game"""
        # Clear all game objects
        self.all_bullets.clear()
        self.all_rockets.clear()
        self.all_asteroids.clear()
        self.all_ships.clear()
        self.all_ai.clear()
        self.radar_signatures.clear()
        self.explosion_events.clear()

        # Reset game state
        self.victory = False
        self.defeat = False

        # Restart the game
        self.setup_game()

    def render(self):
        self.camera.follow_target(self.ship.x, self.ship.y)

        """Render all game elements"""
        self.world_render.draw_stars_tiled(self.camera, self.camera.screen_width, self.camera.screen_width)
        self.world_render.draw_ships(self.all_ships, self.camera)
        self.world_render.draw_rockets(self.all_rockets, self.camera)
        self.world_render.draw_bullets(self.all_bullets, self.camera)
        self.world_render.draw_asteroids(self.all_asteroids, self.camera)
        self.world_render.draw_explosions(self.explosion_events, self.camera)
        self.explosion_events.clear()
        if self.all_ships:  # Make sure we have ships before accessing index 0
            self.world_render.draw_radar_screen(self.radar_signatures, self.ship.enemy_radar_ping_coordinates,
                                                (self.all_ships[0].x, self.all_ships[0].y), self.all_rockets)
        if self.ship:
            self.world_render.draw_ship_data(self.ship)
        self.world_render.draw_fps(self.clock)
        self.world_render.draw_reticle(self.camera)

    def inject_inputs(self, inputs):
        """Receive input data from client"""
        self.inputs = inputs

    def inject_server_data(self, server_messages, dt):
        """Handle multiplayer server data"""
        for message in server_messages:

            # We need to remove our ship from the server update, so we can use the lerp.
            server_ships = message.get('ships', [])
            for server_ship in server_ships:
                if server_ship.owner != self.player_number:
                    # Find and replace the corresponding ship in your list
                    for i, local_ship in enumerate(self.all_ships):
                        if local_ship.owner == server_ship.owner:
                            self.all_ships[i] = server_ship
                            break
                    else:
                        # New ship not in our list yet
                        self.all_ships.append(server_ship)

            self.all_rockets = message.get('rockets', self.all_rockets)
            self.all_bullets = message.get('bullets', self.all_bullets)
            self.all_asteroids = message.get('asteroids', self.all_asteroids)
            self.explosion_events.extend(message.get('explosions', []))

            # We need to check for collision events, so we can start listening to the server again.
            collision_events = message.get('collision_events', [])
            for collision_event in collision_events:
                if collision_event['player_id'] == self.ship.owner:
                    print("Server saw a collision")
                    self.server_saw_collision = True
                    break

            ships = message.get('ships', [])
            for ship in ships:
                if ship.owner == self.player_number:
                    self.ship.shield = ship.shield
                    self.ship.health = ship.health
                    self.interpolate(ship, dt)
                    break

    def interpolate(self, ship, dt):
        """Interpolate player ship position for multiplayer with smooth predictive correction."""

        # Base parameters
        position_error_margin = 75
        velocity_error_margin = 10
        correction_strength = 0.1
        periodic_correction_strength = 0.25

        # Predict server position based on velocity
        predicted_x = ship.x + ship.dx * dt
        predicted_y = ship.y + ship.dy * dt

        # Periodic stronger correction every 120 frames
        if self.frame % 120 == 0:
            x_error = predicted_x - self.ship.x
            y_error = predicted_y - self.ship.y
            self.ship.x += x_error * periodic_correction_strength
            self.ship.y += y_error * periodic_correction_strength

        x_error = predicted_x - self.ship.x
        y_error = predicted_y - self.ship.y
        dx_error = ship.dx - self.ship.dx
        dy_error = ship.dy - self.ship.dy

        x_diff = abs(x_error)
        y_diff = abs(y_error)
        dx_diff = abs(dx_error)
        dy_diff = abs(dy_error)

        if x_diff > position_error_margin or y_diff > position_error_margin:
            scale = min(1.0, max(x_diff, y_diff) / position_error_margin)
            self.ship.x += x_error * correction_strength * scale
            self.ship.y += y_error * correction_strength * scale
        else:
            self.ship.x += x_error * correction_strength
            self.ship.y += y_error * correction_strength

        # Velocity correction
        if dx_diff > velocity_error_margin or dy_diff > velocity_error_margin:
            scale = min(1.0, max(dx_diff, dy_diff) / velocity_error_margin)
            self.ship.dx += dx_error * correction_strength * scale
            self.ship.dy += dy_error * correction_strength
        else:
            self.ship.dx += dx_error * correction_strength
            self.ship.dy += dy_error * correction_strength

        if self.server_saw_collision:
            print("Accepting dx dy from server state.")
            self.ship.dx = ship.dx
            self.ship.dy = ship.dy
            self.server_saw_collision = False


2
