import time
from entities.ship import Ship

from networking.network_simulator import NetworkSimulator
from shared_util.projectile_logic import *
from shared_util.asteroid_logic import *
from shared_util.radar_logic import *
from shared_util.object_handling import *
from shared_util.ship_logic import *


class Server:
    def __init__(self, fake_net):
        self.fake_network = fake_net

        self.all_ships = []
        self.all_missiles = []
        self.all_bullets = []
        self.explosion_events = []

        self.all_asteroids = generate_some_asteroids()

        ship1 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 1, None)  # No camera
        ship2 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 2, None)
        self.all_ships = [ship1, ship2]

    def run(self, dt):
        # Process inputs from all clients
        self.process_network_inputs()

        # Update all ships
        for ship in self.all_ships:
            self.handle_player_ship(ship, dt)

        # Handle game objects
        handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events)
        handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
        handle_asteroids(self.all_asteroids)

        # Remove dead ships
        self.handle_ships()

        # Send game state to all clients
        self.send_state_to_all_clients()

    def process_network_inputs(self):
        """Process all incoming input messages from clients"""
        input_messages = self.fake_network.get_server_messages()

        for message in input_messages:
            player_id = message.get('player_id')
            input_data = message.get('input_data')
            timestamp = message.get('timestamp')

            ship = self.get_ship_by_player_id(player_id)
            if not ship:
                continue

            # Apply inputs to the ship
            apply_inputs_to_ship(ship, input_data)

    def get_ship_by_player_id(self, player_id):
        """Find ship belonging to a specific player"""
        for ship in self.all_ships:
            if ship.owner == player_id:
                return ship
        return None

    def handle_player_ship(self, ship, dt):
        """Handle a single player's ship"""
        # Collect projectiles fired by this ship
        self.collect_missiles(ship)
        self.collect_bullets(ship)

        # Update ship state
        ship.update(dt)
        check_ship_collisions(ship, self.all_asteroids)

    def get_game_state(self):
        """Get current game state to send to clients"""
        state = {
            'missiles': self.all_missiles.copy(),
            'bullets': self.all_bullets.copy(),
            'ships': self.all_ships.copy(),
            'asteroids': self.all_asteroids.copy(),
            'explosions': self.explosion_events.copy(),
            'timestamp': time.time()
        }
        self.explosion_events.clear()
        return state

    def send_state_to_all_clients(self):
        """Send game state to all connected clients"""
        game_state = self.get_game_state()

        # For now, send same state to all clients
        # Later you might customize per client
        self.fake_network.send_to_client(game_state)

    def collect_missiles(self, ship):
        """Collect missiles fired by a ship"""
        new_missiles = ship.missiles
        self.all_missiles.extend(new_missiles)
        ship.missiles.clear()

    def collect_bullets(self, ship):
        """Collect bullets fired by a ship"""
        new_bullets = ship.bullets
        self.all_bullets.extend(new_bullets)
        ship.bullets.clear()

    def handle_ships(self):
        """Remove dead ships"""
        ships_to_remove = []
        for ship in self.all_ships:
            if not ship.alive:
                ships_to_remove.append(ship)

        if ships_to_remove:
            remove_objects(ships_to_remove, self.all_ships)
