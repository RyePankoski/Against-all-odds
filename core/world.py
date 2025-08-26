import random
from rendering.render_util import *
from core.settings import *
from entities.asteroid import Asteroid
from lookup_tables import precomputed_angles
from player import Player


def remove_objects(objects_to_remove, object_list):
    for obj in objects_to_remove:
        if obj in object_list:
            object_list.remove(obj)


class StateManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

        self.all_ships = []
        self.all_missiles = []
        self.all_bullets = []
        self.radar_signatures = []
        self.explosion_events = []
        self.players = []

        self.all_asteroids = {}

        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT
        self.star_field = self.init_star_field()

        playerOne = Player(1, True, self.screen, self.clock)
        playerTwo = Player(2, False, self.screen, self.clock)

        self.all_ships.append(playerOne.ship)
        self.all_ships.append(playerTwo.ship)

        self.players.append(playerOne)
        self.players.append(playerTwo)

        self.generate_some_asteroids()

    def run(self):
        self.screen.fill(BLACK)
        self.update_players()
        self.handle_missiles()
        self.handle_bullets()
        self.handle_asteroids()
        pygame.display.flip()

    def update_players(self):
        for player in self.players:
            if player.connected:
                player.inject_data(self.collect_data())
                player.run()
                self.handle_player_ship(player.ship)

    def handle_player_ship(self, ship):
        self.collect_missiles(ship)
        self.collect_bullets(ship)

        if ship.wants_radar_pulse:
            self.radar_pulse(ship)
            ship.wants_radar_pulse = False

    def collect_data(self):
        state = (self.all_missiles.copy(),
                 self.all_bullets.copy(),
                 self.all_ships.copy(),
                 self.all_asteroids.copy(),
                 self.star_field.copy(),
                 self.radar_signatures.copy(),
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

    def handle_missiles(self):
        missiles_to_remove = []

        for missile in self.all_missiles:
            missile.handle_self()
            missile.check_for_collisions(self.all_ships, self.all_asteroids)

            if missile.alive is False:
                missiles_to_remove.append(missile)
                self.explosion_events.append((missile.x, missile.y, YELLOW, 100))
                continue

            # Remove missiles that are way outside the world
            if (missile.x < -100 or missile.x > self.world_width + 100 or
                    missile.y < -100 or missile.y > self.world_height + 100):
                missiles_to_remove.append(missile)

        if len(missiles_to_remove) > 0:
            remove_objects(missiles_to_remove, self.all_missiles)

    def handle_bullets(self):
        bullets_to_remove = []

        for bullet in self.all_bullets:
            bullet.handle_self()
            bullet.check_for_collisions(self.all_ships, self.all_asteroids)

            if bullet.alive is False:
                self.explosion_events.append((bullet.x, bullet.y, CYAN, 10))
                bullets_to_remove.append(bullet)
                continue

            if (bullet.x < -100 or bullet.x > self.world_width + 100 or
                    bullet.y < -100 or bullet.y > self.world_height + 100):
                bullets_to_remove.append(bullet)

        if len(bullets_to_remove) > 0:
            remove_objects(bullets_to_remove, self.all_bullets)

    def handle_asteroids(self):
        asteroids_to_remove = []
        asteroids_to_relocate = []

        for sector, asteroid_list in self.all_asteroids.items():
            for asteroid in asteroid_list[:]:  # Copy list to avoid modification during iteration
                old_sector = asteroid.sector
                asteroid.float_on()
                new_sector = asteroid.sector

                if asteroid.alive is False:
                    asteroids_to_remove.append(asteroid)
                elif old_sector != new_sector:
                    asteroids_to_relocate.append((asteroid, old_sector, new_sector))

        for asteroid, old_sector, new_sector in asteroids_to_relocate:
            if old_sector in self.all_asteroids:
                self.all_asteroids[old_sector].remove(asteroid)

            if new_sector not in self.all_asteroids:
                self.all_asteroids[new_sector] = []
            self.all_asteroids[new_sector].append(asteroid)

        if len(asteroids_to_remove) > 0:
            self.remove_asteroids(asteroids_to_remove)

    def radar_pulse(self, passed_ship):
        radar_rays = precomputed_angles.RADAR_DIRECTIONS[passed_ship.radar_resolution]
        signatures = []
        ray_collision_distance = RADAR_DETECT_RANGE * RADAR_DETECT_RANGE

        for dx, dy in radar_rays:
            ray_distance = 0
            ray_x, ray_y = passed_ship.x, passed_ship.y

            hit_found = False

            while (self.world_width > ray_x > 0 and self.world_height > ray_y > 0
                   and ray_distance < RADAR_PULSE_RANGE and not hit_found):

                ray_distance += RADAR_PULSE_SPEED
                ray_x += (dx * RADAR_PULSE_SPEED)
                ray_y += (dy * RADAR_PULSE_SPEED)
                ray_sector = int(ray_x // SECTOR_SIZE), int(ray_y // SECTOR_SIZE)

                for ship in self.all_ships:
                    if ship == passed_ship:
                        continue

                    distance = ((ship.x - ray_x) ** 2 + (ship.y - ray_y) ** 2)
                    if distance < ray_collision_distance:
                        signatures.append((ray_x, ray_y, RED))
                        hit_found = True
                        break

                if ray_sector in self.all_asteroids and self.all_asteroids[ray_sector]:
                    for asteroid in self.all_asteroids[ray_sector]:
                        distance_squared = ((asteroid.x - ray_x) ** 2 + (asteroid.y - ray_y) ** 2)
                        collision_radius = 20 + asteroid.radius  # Ray detection radius + asteroid radius
                        collision_radius_squared = collision_radius * collision_radius

                        if distance_squared < collision_radius_squared:
                            signatures.append((ray_x, ray_y, WHITE))
                            hit_found = True
                            break

        self.radar_signatures = signatures

    def remove_asteroids(self, asteroids_to_remove):
        asteroids_to_remove_set = set(asteroids_to_remove)

        for sector, asteroid_list in self.all_asteroids.items():
            self.all_asteroids[sector] = [a for a in asteroid_list if a not in asteroids_to_remove_set]

    def init_star_field(self):
        star_field = []

        for x in range(0, self.world_width, 50):
            for y in range(0, self.world_height, 50):
                if random.random() < 0.005:
                    star_field.append((x, y, random.uniform(0.5, 7)))

        return star_field

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
