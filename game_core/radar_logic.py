from lookup_tables import precomputed_angles
from core.settings import *


def radar_pulse(all_ships, all_asteroids, world_width, world_height, passed_ship):

    radar_rays = precomputed_angles.RADAR_DIRECTIONS[passed_ship.radar_resolution]
    signatures = []
    ray_collision_distance = RADAR_DETECT_RANGE * RADAR_DETECT_RANGE

    for dx, dy in radar_rays:
        ray_distance = 0
        ray_x, ray_y = passed_ship.x, passed_ship.y
        hit_found = False

        while (0 < ray_x < world_width and 0 < ray_y < world_height
               and ray_distance < RADAR_PULSE_RANGE and not hit_found):

            ray_distance += RADAR_PULSE_SPEED
            ray_x += dx * RADAR_PULSE_SPEED
            ray_y += dy * RADAR_PULSE_SPEED
            ray_sector = int(ray_x // SECTOR_SIZE), int(ray_y // SECTOR_SIZE)

            for ship in all_ships:
                if ship == passed_ship:
                    continue

                distance = ((ship.x - ray_x) ** 2 + (ship.y - ray_y) ** 2)
                if distance < ray_collision_distance:
                    signatures.append((ray_x, ray_y, RED))
                    hit_found = True
                    break

            if ray_sector in all_asteroids and all_asteroids[ray_sector]:
                for asteroid in all_asteroids[ray_sector]:
                    distance_squared = ((asteroid.x - ray_x) ** 2 +
                                        (asteroid.y - ray_y) ** 2)
                    collision_radius = 20 + asteroid.radius
                    collision_radius_squared = collision_radius ** 2

                    if distance_squared < collision_radius_squared:
                        signatures.append((ray_x, ray_y, WHITE))
                        hit_found = True
                        break

    return signatures
