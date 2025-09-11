from rendering.camera import Camera
from entities.ships.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from ship_subsystems.radar_system import RadarSystem
from game.ai import AI
from client_scenes.victory_screen import VictoryScreen
from client_scenes.defeat_screen import DefeatScreen
from rendering.world_render import WorldRender
from rendering.sound_manager import SoundManager
from entities.ships.battleship import BattleShip


class MainScene:
    def __init__(self, screen, clock, connected, player_id=None):
        self.ship = None
        self.screen = screen
        self.clock = clock
        self.connected = connected

        if self.connected:
            self.player_number = player_id
        else:
            self.player_number = random.randint(0, 10)

        # Game state
        self.victory = False
        self.defeat = False
        self.inputs = {}

        # Game objects
        self.all_projectiles = []
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
        self.sound = SoundManager()

        # Game systems
        self.radar_system = RadarSystem()

        # UI components
        self.victory_screen = VictoryScreen(self.screen)
        self.defeat_screen = DefeatScreen(self.screen)
        self.world_render = WorldRender(self.screen)

        self.chosen_spectate = False
        self.spectate_ship_address = None

        # AI configuration
        self.number_of_ai = 1
        self.ai_difficulty = 5

        # if self.ai_difficulty > 4:
        #     self.number_of_ai += 1

        # Initialize game
        self.setup_game()
        self.current_asteroids = MAX_ASTEROIDS

    def setup_game(self):
        """Initialize the game world and entities"""
        # Create player ship
        self.ship = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, self.player_number,  self.camera)
        self.all_ships.append(self.ship)

        if not self.connected:
            self.all_asteroids = generate_some_asteroids(MAX_ASTEROIDS)

        # Create AI ships if in single player
        self.spawn_ai_ships()

    def spawn_ai_ships(self):
        """Create AI ships for single player mode"""
        if not self.connected:

            battleship = BattleShip(WORLD_WIDTH / 2 + 1000, WORLD_HEIGHT / 2)
            self.all_ships.append(battleship)

            for _ in range(self.number_of_ai):
                ai_ship = Ship(
                    random.randint(0, WORLD_WIDTH),
                    random.randint(0, WORLD_HEIGHT),
                    -1,
                    None
                )
                self.all_ships.append(ai_ship)
                ai = AI(ai_ship, self.ship, self.all_ships, self.all_asteroids, self.ai_difficulty, self.screen,
                        self.camera)
                self.all_ai.append(ai)

    def run(self, dt):
        """Main game loop - handles all game updates and rendering"""
        self.frame += 1
        self.check_game_state()

        if self.ship and not self.defeat:
            self.update_player_ship(dt)

        if not self.connected and not self.defeat:
            self.update_game_objects()
            self.update_ai(dt)

        if self.defeat and self.chosen_spectate:
            self.update_spectate_target()

        self.render()
        self.handle_victory_screen()
        self.handle_defeat_screen()
        self.world_render.draw_reticle(self.camera)

    def update_ai(self, dt):
        """Update AI and remove dead ones"""
        for ai in self.all_ai[:]:  # Copy list to avoid modification during iteration
            ai.run(dt)
            if not ai.ship.alive:
                self.all_ai.remove(ai)

        for ship in self.all_ships:
            if isinstance(ship, BattleShip):
                ship.run(dt)

    def check_game_state(self):
        """Check win/lose conditions"""
        if len(self.all_ai) <= 0 and not self.connected:
            self.victory = True

        if self.ship and self.ship.health <= 0:
            self.ship = None
            self.defeat = True

    def update_player_ship(self, dt):
        """Update player ship and handle radar"""
        self.ship.run(dt)
        apply_inputs_to_ship(self.ship, self.inputs)
        self.handle_sounds(self.inputs)

        if not self.connected and self.all_asteroids:
            check_ship_collisions(self.ship, self.all_asteroids)

        # Handle radar pulse
        if self.ship.is_radar_on:
            if self.ship.can_radar_pulse:
                self.radar_signatures.clear()
                self.radar_system.begin_scan(self.ship, self.all_ships, self.all_asteroids)
                self.ship.can_radar_pulse = False
                self.ship.enemy_radar_ping_coordinates.clear()

        if self.radar_system.scanning:
            self.radar_signatures.extend(self.radar_system.continue_scan())

    def update_game_objects(self):
        """Update all game objects and handle collisions"""
        # Handle collisions and physics
        asteroid_diff = handle_asteroids(self.all_asteroids)
        self.current_asteroids -= asteroid_diff

        if self.current_asteroids < MAX_ASTEROIDS:
            for _ in range(asteroid_diff):
                spawn_single_asteroid(self.all_asteroids)
                self.current_asteroids += 1

        # Collect projectiles from ships
        self.collect_projectiles()
        # Update projectiles
        self.update_projectiles()
        # Remove dead ships
        self.remove_dead_ships()

    def collect_projectiles(self):
        """Collect projectiles from all ships"""
        for ship in self.all_ships:
            self.all_projectiles.extend(ship.all_projectiles)
            ship.all_projectiles.clear()

    def update_projectiles(self):
        """Update all projectiles and handle collisions"""
        handle_projectile(self.all_projectiles, self.all_ships, self.all_asteroids, self.explosion_events)

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
                self.victory_screen.state_to_extract = "stay"
                self.reset_game()

    def handle_defeat_screen(self):
        if self.defeat:
            if not self.connected:
                self.defeat_screen.run()
                if self.defeat_screen.state_to_extract == "new_game":
                    self.defeat_screen.state_to_extract = "stay"
                    self.reset_game()
            else:
                # Spectate mode for single player
                if not self.chosen_spectate and self.all_ships:
                    # Pick a random ship to follow that isn't the player's dead ship
                    live_ships = [s for s in self.all_ships if s.alive]
                    if live_ships:
                        self.spectate_ship_address = random.choice(live_ships).owner
                        self.chosen_spectate = True
                # Disable inputs
                self.inputs.clear()

    def reset_game(self):
        """Reset game state for new game"""
        self.all_projectiles.clear()
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
        """Render all game elements"""
        self.world_render.draw_stars_tiled(self.camera, self.camera.screen_width, self.camera.screen_width)
        self.world_render.draw_ships(self.all_ships, self.camera)
        self.world_render.draw_projectiles(self.all_projectiles, self.camera)
        self.world_render.draw_asteroids(self.all_asteroids, self.camera)
        self.world_render.draw_explosions(self.explosion_events, self.camera)
        self.explosion_events.clear()

        if self.ship and not self.defeat:
            self.camera.follow_target(self.ship.x, self.ship.y)
            self.world_render.draw_ship_data(self.ship)
            self.world_render.draw_radar_screen(self.radar_signatures, self.ship.enemy_radar_ping_coordinates,
                                                (self.all_ships[0].x, self.all_ships[0].y), self.all_projectiles)
        elif self.chosen_spectate and self.spectate_ship_address is not None:
            spectate_ship = next((s for s in self.all_ships if s.owner == self.spectate_ship_address), None)
            if spectate_ship:
                self.camera.follow_target(spectate_ship.x, spectate_ship.y)

        self.world_render.draw_fps(self.clock)

    def update_spectate_target(self):
        if self.chosen_spectate:
            spectate_ship = next((s for s in self.all_ships if s.owner == self.spectate_ship_address and s.alive), None)
            if spectate_ship is None:
                # Spectated ship is dead or removed, pick a new live ship
                live_ships = [s for s in self.all_ships if s.alive and s.owner != self.player_number]
                if live_ships:
                    self.spectate_ship_address = random.choice(live_ships).owner
                else:
                    # No live ships left, optional: stop spectating
                    self.chosen_spectate = False
                    self.spectate_ship_address = None

    def inject_inputs(self, inputs):
        """Receive input data from client"""
        if isinstance(inputs, dict) and "type" in inputs:
            if inputs["type"] == "PLAYER_INPUT":
                self.inputs = inputs["input_data"]  # Changed from "data" to "input_data"
            else:
                return
        else:
            self.inputs = []

    def inject_server_data(self, message, dt):
        """Handle multiplayer server data"""

        # We need to remove our ship from the server update, so we can use the lerp.
        server_ships = message.get('s', [])  # Changed from 'ships' to 's'

        # Update/add ships from server (convert from dict if needed)
        for server_ship_data in server_ships:
            if hasattr(server_ship_data, 'owner'):
                server_ship = server_ship_data
            else:
                server_ship = Ship(server_ship_data['x'], server_ship_data['y'], server_ship_data['o'],
                                   None)  # Changed 'owner' to 'o'
                server_ship.dx = server_ship_data.get('dx', 0)
                server_ship.dy = server_ship_data.get('dy', 0)
                server_ship.health = server_ship_data.get('h', 100)  # Changed 'health' to 'h'
                server_ship.shield = server_ship_data.get('s', 100)  # Changed 'shield' to 's'
                server_ship.facing_angle = server_ship_data.get('a', 0)  # Changed 'angle' to 'a'
                server_ship.owner_name = server_ship_data.get('n', None)

            ship_owner = server_ship.owner if hasattr(server_ship, 'owner') else server_ship_data[
                'o']  # Changed 'owner' to 'o'

            if ship_owner != self.player_number:  # Compare addresses
                found = False
                for i, local_ship in enumerate(self.all_ships):
                    if local_ship.owner == ship_owner:
                        self.all_ships[i] = server_ship
                        found = True
                        break
                if not found:
                    self.all_ships.append(server_ship)

        server_owners = {ship.owner if hasattr(ship, 'owner') else ship['o'] for ship in
                         server_ships}  # Changed 'owner' to 'o'
        server_owners.add(self.player_number)  # Keep your own ship
        self.all_ships = [ship for ship in self.all_ships if ship.owner in server_owners]

        # Handle projectiles - convert dict data to objects for rendering
        if 'p' in message:
            self.all_projectiles = message['p']  # Changed from 'projectiles' to 'p'

        if 'a' in message:
            asteroids = {}
            for sector_str, asteroid_list in message['a'].items():  # Changed from 'asteroids' to 'a'
                x, y = map(float, sector_str.split(','))
                sector_key = (int(x), int(y))
                asteroids[sector_key] = asteroid_list  # Just use the dicts directly
            self.all_asteroids = asteroids

        self.explosion_events.extend(message.get('e', []))  # Changed from 'explosions' to 'e'

        collision_events = message.get('c', [])  # Changed from 'collision_events' to 'c'
        for collision_event in collision_events:
            if collision_event['player_id'] == self.player_number:  # Compare with our player_id
                print("Server saw a collision")
                self.server_saw_collision = True
                break

        # Update our ship's health/shield from server
        ships = message.get('s', [])
        for ship_data in ships:
            ship_owner = ship_data.owner if hasattr(ship_data, 'owner') else ship_data['o']  # Changed 'owner' to 'o'
            if ship_owner == self.player_number:  # Find our ship
                if self.ship:  # Make sure we have a ship
                    self.ship.shield = ship_data.shield if hasattr(ship_data, 'shield') else ship_data.get('s',
                                                                                                           100)  # Changed 'shield' to 's'
                    self.ship.health = ship_data.health if hasattr(ship_data, 'health') else ship_data.get('h',
                                                                                                           100)  # Changed 'health' to 'h'
                    self.interpolate(ship_data, dt)
                break

    def interpolate(self, ship_data, dt):
        """Interpolate player ship position for multiplayer with smooth predictive correction."""
        # Base parameters
        position_error_margin = 75
        velocity_error_margin = 50
        correction_strength = 0.025
        periodic_correction_strength = 0.05

        # Extract values from ship data (could be dict or object)
        ship_x = ship_data.x if hasattr(ship_data, 'x') else ship_data['x']
        ship_y = ship_data.y if hasattr(ship_data, 'y') else ship_data['y']
        ship_dx = ship_data.dx if hasattr(ship_data, 'dx') else ship_data.get('dx', 0)
        ship_dy = ship_data.dy if hasattr(ship_data, 'dy') else ship_data.get('dy', 0)

        # Predict server position based on velocity
        predicted_x = ship_x + ship_dx * dt
        predicted_y = ship_y + ship_dy * dt

        # Periodic stronger correction every 120 frames
        if self.frame % 120 == 0:
            x_error = predicted_x - self.ship.x
            y_error = predicted_y - self.ship.y
            self.ship.x += x_error * periodic_correction_strength
            self.ship.y += y_error * periodic_correction_strength

        x_error = predicted_x - self.ship.x
        y_error = predicted_y - self.ship.y
        dx_error = ship_dx - self.ship.dx
        dy_error = ship_dy - self.ship.dy

        x_diff = abs(x_error)
        y_diff = abs(y_error)
        dx_diff = abs(dx_error)
        dy_diff = abs(dy_error)

        if x_diff > position_error_margin or y_diff > position_error_margin:
            # print("Correcting pos")
            scale = min(1.0, max(x_diff, y_diff) / position_error_margin)
            self.ship.x += x_error * correction_strength * scale
            self.ship.y += y_error * correction_strength * scale
        else:
            self.ship.x += x_error * correction_strength
            self.ship.y += y_error * correction_strength

        # Velocity correction
        if dx_diff > velocity_error_margin or dy_diff > velocity_error_margin:
            # print("Correcting vel")
            scale = min(1.0, max(dx_diff, dy_diff) / velocity_error_margin)
            self.ship.dx += dx_error * correction_strength * scale
            self.ship.dy += dy_error * correction_strength * scale
        else:
            self.ship.dx += dx_error * correction_strength
            self.ship.dy += dy_error * correction_strength

        if self.server_saw_collision:
            print("Accepting dx dy from server state.")
            self.ship.dx = ship_dx
            self.ship.dy = ship_dy
            self.server_saw_collision = False

    def handle_sounds(self, inputs):
        if inputs.get('mouse_left'):
            if self.ship and self.ship.current_weapon == "bullet":
                self.sound.start_gunfire()
            if self.ship and self.ship.current_weapon == "rocket":
                self.sound.play_rocket_sound()
        else:
            self.sound.stop_gunfire_with_fade()
