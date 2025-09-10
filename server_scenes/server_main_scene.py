import time
from entities.ships.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from entities.ships.battleship import BattleShip


class ServerMainScene:
    def __init__(self):
        self.all_ships = []
        self.all_projectiles = []
        self.explosion_events = []
        self.all_asteroids = generate_some_asteroids(MAX_ASTEROIDS)
        self.current_asteroids = MAX_ASTEROIDS

        # Create ships
        ship1 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 1, None)
        ship2 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 2, None)
        battleship = BattleShip(WORLD_WIDTH / 2 + 100, WORLD_HEIGHT / 2 + 100)
        self.all_ships = [ship1, ship2, battleship]

    def step(self, dt, input_messages):

        for message in input_messages:
            player_id = message.get('player_id')
            input_data = message.get('input_data')

            # Find player's ship and apply inputs
            for ship in self.all_ships:
                if ship.owner == player_id:
                    apply_inputs_to_ship(ship, input_data)
                    break

        collision_events = []

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
            'all_projectiles': self.all_projectiles,
            'ships': self.all_ships.copy(),
            'asteroids': self.all_asteroids,
            'explosions': self.explosion_events.copy(),
            'timestamp': time.time(),
            'collision_events': collision_events
        }
        self.explosion_events.clear()
        return game_state
