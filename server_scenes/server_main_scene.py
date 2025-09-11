import random
import time
from entities.ships.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from entities.ships.battleship import BattleShip


class ServerMainScene:
    def __init__(self, connected_players=None):
        self.connected_players = connected_players
        self.all_ships = []
        self.all_projectiles = []
        self.explosion_events = []
        self.all_asteroids = generate_some_asteroids(MAX_ASTEROIDS)
        self.current_asteroids = MAX_ASTEROIDS
        if self.connected_players:
            self.create_player_ships()

    def create_player_ships(self):
        for address in self.connected_players:  # address is the key
            player_info = self.connected_players[address]
            ship = Ship(
                random.randint(0, WORLD_WIDTH),
                random.randint(0, WORLD_HEIGHT),
                address,  # unique ID / address
                None
            )
            ship.owner_name = player_info['player_name']  # get the name from the dict
            self.all_ships.append(ship)

    def step(self, input_messages, dt):
        collision_events = []

        # Apply inputs to ships
        for message in input_messages:
            player_id = message.get('player_id')  # This is the network address
            input_data = message.get('input_data')

            # Find player's ship and apply inputs
            for ship in self.all_ships:
                if ship.owner == player_id:  # Match network address
                    apply_inputs_to_ship(ship, input_data)
                    break

        # Update all ships
        for ship in self.all_ships:
            ship.run(dt)

            if check_ship_collisions(ship, self.all_asteroids):
                collision_events.append({
                    'player_id': ship.owner,
                    'collision_type': 'asteroid',
                })

            # Collect new projectiles
            self.all_projectiles.extend(ship.all_projectiles)
            ship.all_projectiles.clear()

        # Update game objects
        handle_projectile(self.all_projectiles, self.all_ships, self.all_asteroids, self.explosion_events)

        # Handle asteroids
        asteroid_diff = handle_asteroids(self.all_asteroids)
        self.current_asteroids -= asteroid_diff

        if self.current_asteroids < MAX_ASTEROIDS:
            for _ in range(asteroid_diff):
                spawn_single_asteroid(self.all_asteroids)
                self.current_asteroids += 1

        self.all_ships = [ship for ship in self.all_ships if ship.alive]

        # Send state to clients
        game_state = {
            'projectiles': self.all_projectiles,
            'ships': self.all_ships.copy(),
            'asteroids': self.all_asteroids,
            'explosions': self.explosion_events.copy(),
            'timestamp': time.time(),
            'collision_events': collision_events
        }
        self.explosion_events.clear()
        return game_state
