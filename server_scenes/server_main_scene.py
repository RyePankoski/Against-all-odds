import time
from entities.ship import Ship
from shared_util.ship_logic import *
from shared_util.asteroid_logic import *
from shared_util.projectile_logic import *
from entities.battleship import BattleShip


class ServerMainScene:
    def __init__(self, fake_net):
        self.fake_network = fake_net
        self.all_ships = []

        self.all_rockets = []
        self.all_bullets = []
        self.explosion_events = []
        self.all_asteroids = generate_some_asteroids()

        # Create ships
        ship1 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 1, None)
        ship2 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 2, None)

        battleship = BattleShip(WORLD_WIDTH / 2 + 100, WORLD_HEIGHT / 2 + 100)

        self.all_ships = [ship1, ship2, battleship]

    def run(self, dt):
        input_messages = self.fake_network.get_server_messages()
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
            self.all_bullets.extend(ship.bullets)
            self.all_rockets.extend(ship.rockets)
            ship.bullets.clear()
            ship.rockets.clear()

        # Update game objects
        handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events)
        handle_rockets(self.all_rockets, self.all_ships, self.all_asteroids, self.explosion_events)
        handle_asteroids(self.all_asteroids)

        # Remove dead ships
        self.all_ships = [ship for ship in self.all_ships if ship.alive]

        # Send state to clients
        game_state = {
            'rockets': self.all_rockets.copy(),
            'bullets': self.all_bullets.copy(),
            'ships': self.all_ships.copy(),
            'asteroids': self.all_asteroids,
            'explosions': self.explosion_events.copy(),
            'timestamp': time.time(),
            'collision_events': collision_events
        }
        self.explosion_events.clear()
        self.fake_network.send_to_client(game_state)
