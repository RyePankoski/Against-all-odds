from game.settings import *
from lookup_tables import precomputed_angles
import math


class RadarSystem:
    def __init__(self):

        self.current_frame = 1
        self.scan_frames = 100
        self.current_ray = 0

        self.scan_resolution = 720
        self.passed_ship = None
        self.all_ships = None
        self.all_asteroids = None
        self.rays_per_frame = None
        self.radar_rays = None

        self.scanning = False
        self.ray_collision_distance_squared = RADAR_DETECT_RANGE * RADAR_DETECT_RANGE

    def begin_scan(self, passed_ship, all_ships, all_asteroids):
        self.scanning = True
        self.current_frame = 1
        self.current_ray = 0
        self.passed_ship = passed_ship
        self.all_ships = all_ships
        self.all_asteroids = all_asteroids
        self.scan_resolution = passed_ship.radar_resolution

        # We cant have < 1 rays per frame
        if self.scan_resolution < self.scan_frames:
            self.scan_frames = self.scan_resolution
        else:
            self.scan_frames = 100

        self.radar_rays = precomputed_angles.RADAR_DIRECTIONS[self.scan_resolution]
        self.rays_per_frame = self.scan_resolution // self.scan_frames
        print(self.scan_resolution)

    def continue_scan(self):
        signatures = []

        if self.current_frame >= self.scan_frames:
            self.scanning = False

        # Only process some % of total rays per frame.
        while self.current_ray < self.rays_per_frame * self.current_frame:

            dx, dy = self.radar_rays[self.current_ray]
            self.current_ray += 1

            ray_distance = 0
            ray_x, ray_y = self.passed_ship.x, self.passed_ship.y
            hit_found = False

            while (0 < ray_x < WORLD_WIDTH and 0 < ray_y < WORLD_HEIGHT
                   and ray_distance < RADAR_PULSE_RANGE and not hit_found):

                ray_distance += RADAR_PULSE_SPEED
                ray_x += dx * RADAR_PULSE_SPEED
                ray_y += dy * RADAR_PULSE_SPEED
                ray_sector = int(ray_x // SECTOR_SIZE), int(ray_y // SECTOR_SIZE)

                for ship in self.all_ships:
                    if ship is self.passed_ship:
                        continue

                    distance_squared = ((ship.x - ray_x) ** 2 + (ship.y - ray_y) ** 2)
                    if distance_squared < self.ray_collision_distance_squared:

                        angle = math.atan2(
                            ship.y - self.passed_ship.y,  # Δy first
                            ship.x - self.passed_ship.x  # Δx second
                        )
                        ship.enemy_radar_ping_coordinates.append(angle)

                        signatures.append((ray_x, ray_y, RED))
                        hit_found = True
                        break

                if ray_sector in self.all_asteroids and self.all_asteroids[ray_sector]:
                    for asteroid in self.all_asteroids[ray_sector]:
                        distance_squared = ((asteroid.x - ray_x) ** 2 +
                                            (asteroid.y - ray_y) ** 2)

                        if distance_squared < self.ray_collision_distance_squared:
                            signatures.append((ray_x, ray_y, WHITE))
                            hit_found = True
                            break

        self.current_frame += 1
        return signatures
