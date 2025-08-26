import math
import random
from entities.ship import Ship
from entities.asteroid import Asteroid
from networking.network_simulator import NetworkSimulator
from game_core.projectile_logic import *
from game_core.asteroid_logic import *
from game_core.radar_logic import *
from game_core.object_handling import *
from game_core.ship_logic import *


class Server:
    def __init__(self):
        self.fake_network = NetworkSimulator()

        self.all_ships = []
        self.all_missiles = []
        self.all_bullets = []
        self.explosion_events = []

        self.all_asteroids = {}
        self.generate_some_asteroids()

        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT

        ship1 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 1, None)  # No camera
        ship2 = Ship(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, 2, None)
        self.all_ships = [ship1, ship2]

    def run(self):
        handle_missiles(self.all_missiles, self.all_ships, self.all_asteroids, self.explosion_events,
                        self.world_width, self.world_height)
        handle_bullets(self.all_bullets, self.all_ships, self.all_asteroids, self.explosion_events,
                       self.world_width, self.world_height)
        handle_asteroids(self.all_asteroids)

    def process_network_inputs(self, network_simulator):
        """Process all incoming input messages from clients"""
        input_messages = network_simulator.get_server_messages()

        for message in input_messages:
            player_id = message.get('player_id')
            input_data = message.get('input_data')
            timestamp = message.get('timestamp')

            # Find the ship belonging to this player
            ship = self.get_ship_by_player_id(player_id)
            if not ship:
                continue

            # Apply inputs to the ship
            self.apply_inputs_to_ship(ship, input_data)

    def apply_inputs_to_ship(self, ship, input_data):
        """Apply input data to a ship (server-side processing)"""
        # Movement inputs
        thrust = BOOST_THRUST if input_data.get('shift') and ship.current_boost_fuel > 0 else THRUST

        if input_data.get('w'):
            ship.dy -= thrust
        if input_data.get('a'):
            ship.dx -= thrust
        if input_data.get('s'):
            ship.dy += thrust
        if input_data.get('d'):
            ship.dx += thrust
        if input_data.get('space'):
            ship.brake()

        # Handle boost fuel
        if input_data.get('shift') and ship.current_boost_fuel > 0:
            ship.current_boost_fuel -= 1
        elif not input_data.get('shift') and ship.current_boost_fuel < BOOST_FUEL:
            ship.current_boost_fuel += 0.01

        # Weapon selection
        if input_data.get('1'):
            ship.current_weapon = "missile"
        if input_data.get('2'):
            ship.current_weapon = "bullet"

        # Firing
        if input_data.get('mouse_left'):
            if ship.current_weapon == "missile" and ship.can_fire_missile:
                fire_weapon(ship, "missile")
                ship.can_fire_missile = False
            elif ship.current_weapon == "bullet" and ship.can_fire_bullet:
                fire_weapon(ship, "bullet")
                ship.can_fire_bullet = False

        # Control panel
        if input_data.get('x') and ship.can_input_controls:
            ship.dampening_active = not ship.dampening_active
            ship.can_input_controls = False
        if input_data.get('r') and ship.can_pulse:
            ship.wants_radar_pulse = True
            ship.can_pulse = False

        # Update ship facing angle based on mouse position
        if input_data.get('mouse_world_pos'):
            update_ship_facing(ship, input_data['mouse_world_pos'])

    def get_ship_by_player_id(self, player_id):
        """Find ship belonging to a specific player"""
        for ship in self.all_ships:
            if ship.owner == player_id:
                return ship
        return None

    def handle_player_ship(self, ship, player):
        self.collect_missiles(ship)
        self.collect_bullets(ship)

        if ship.wants_radar_pulse:
            signatures = radar_pulse(ship, self.all_asteroids, self.all_ships, self.all_missiles, self.all_bullets)
            player.set_radar_signatures(signatures)
            ship.wants_radar_pulse = False

    def get_game_state(self):
        state = (self.all_missiles.copy(),
                 self.all_bullets.copy(),
                 self.all_ships.copy(),
                 self.all_asteroids.copy(),
                 self.explosion_events.copy()
                 )
        self.explosion_events.clear()

        return state

    def collect_missiles(self, ship):
        new_missiles = ship.missiles
        self.all_missiles.extend(new_missiles)
        ship.missiles.clear()

    def collect_bullets(self, ship):
        new_bullets = ship.bullets
        self.all_bullets.extend(new_bullets)
        ship.bullets.clear()

    def handle_ships(self):
        ships_to_remove = []
        for ship in self.all_ships:
            if ship.alive is False:
                ships_to_remove.append(ship)

        if len(ships_to_remove) > 0:
            remove_objects(ships_to_remove, self.all_ships)

    def generate_some_asteroids(self):
        for _ in range(100):
            sectorX = (self.world_width / 2 + 200) // SECTOR_SIZE
            sectorY = (self.world_height / 2 + 200) // SECTOR_SIZE

            asteroid = Asteroid(self.world_width / 2 + 200, self.world_height / 2 + 200,
                                random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(30, 100),
                                (self.world_width, self.world_height), (sectorX, sectorY))

            if (sectorX, sectorY) in self.all_asteroids:
                self.all_asteroids[(sectorX, sectorY)].append(asteroid)
            else:
                self.all_asteroids[(sectorX, sectorY)] = [asteroid]
