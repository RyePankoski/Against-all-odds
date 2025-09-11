from shared_util.object_handling import *
from game.settings import *
from entities.world_entities.asteroid import Asteroid
import random


def handle_asteroids(all_asteroids):
    asteroids_to_remove = []
    asteroids_to_relocate = []
    sum_of_removed_asteroids = 0

    for sector, asteroid_list in all_asteroids.items():
        for asteroid in asteroid_list[:]:
            old_sector = asteroid.sector
            asteroid.float_on()
            new_sector = asteroid.sector

            if not asteroid.alive:
                asteroids_to_remove.append(asteroid)
                sum_of_removed_asteroids += 1
            elif old_sector != new_sector:
                asteroids_to_relocate.append((asteroid, old_sector, new_sector))

    for asteroid, old_sector, new_sector in asteroids_to_relocate:
        if old_sector in all_asteroids:
            all_asteroids[old_sector].remove(asteroid)

        if new_sector not in all_asteroids:
            all_asteroids[new_sector] = []
        all_asteroids[new_sector].append(asteroid)

    if asteroids_to_remove:
        remove_objects(asteroids_to_remove, all_asteroids)

    empty_sectors = [sector for sector, asteroid_list in all_asteroids.items() if not asteroid_list]
    for sector in empty_sectors:
        del all_asteroids[sector]

    return sum_of_removed_asteroids


def get_nearby_asteroids(all_asteroids, all_ships, radius=CAMERA_VIEW_WIDTH):
    nearby_asteroids = {}
    radius_sq = radius ** 2
    for sector, asteroid_list in all_asteroids.items():
        filtered = []
        for asteroid in asteroid_list:
            if not asteroid.alive:
                continue
            for ship in all_ships:
                dx = ship.x - asteroid.x
                dy = ship.y - asteroid.y
                if dx * dx + dy * dy <= radius_sq:
                    filtered.append({'x': asteroid.x, 'y': asteroid.y, 'radius': asteroid.radius})
                    break

        if filtered:
            nearby_asteroids[sector] = filtered
    return nearby_asteroids


def generate_some_asteroids(number_of_asteroids):
    asteroids = {}
    margin = 100  # Distance outside the screen bounds

    for _ in range(number_of_asteroids):
        # Randomly choose which edge to spawn from
        edge = random.choice(['top', 'bottom', 'left', 'right'])

        if edge == 'top':
            x = random.uniform(-margin, WORLD_WIDTH + margin)
            y = -margin
            vel_y = random.uniform(0.2, 1.0)  # Move downward
            vel_x = random.uniform(-0.5, 0.5)
        elif edge == 'bottom':
            x = random.uniform(-margin, WORLD_WIDTH + margin)
            y = WORLD_HEIGHT + margin
            vel_y = random.uniform(-1.0, -0.2)  # Move upward
            vel_x = random.uniform(-0.5, 0.5)
        elif edge == 'left':
            x = -margin
            y = random.uniform(-margin, WORLD_HEIGHT + margin)
            vel_x = random.uniform(0.2, 1.0)  # Move rightward
            vel_y = random.uniform(-0.5, 0.5)
        else:  # right
            x = WORLD_WIDTH + margin
            y = random.uniform(-margin, WORLD_HEIGHT + margin)
            vel_x = random.uniform(-1.0, -0.2)  # Move leftward
            vel_y = random.uniform(-0.5, 0.5)

        sectorX = x // SECTOR_SIZE
        sectorY = y // SECTOR_SIZE

        asteroid = Asteroid(x, y, vel_x, vel_y, random.uniform(50, 200),
                            (WORLD_WIDTH, WORLD_HEIGHT), (sectorX, sectorY))

        if (sectorX, sectorY) in asteroids:
            asteroids[(sectorX, sectorY)].append(asteroid)
        else:
            asteroids[(sectorX, sectorY)] = [asteroid]

    return asteroids


def spawn_single_asteroid(existing_asteroids):
    margin = 100  # Distance outside the screen bounds

    # Randomly choose which edge to spawn from
    edge = random.choice(['top', 'bottom', 'left', 'right'])

    if edge == 'top':
        x = random.uniform(-margin, WORLD_WIDTH + margin)
        y = -margin
        vel_y = random.uniform(0.2, 1.0)  # Move downward into screen
        vel_x = random.uniform(-0.5, 0.5)
    elif edge == 'bottom':
        x = random.uniform(-margin, WORLD_WIDTH + margin)
        y = WORLD_HEIGHT + margin
        vel_y = random.uniform(-1.0, -0.2)  # Move upward into screen
        vel_x = random.uniform(-0.5, 0.5)
    elif edge == 'left':
        x = -margin
        y = random.uniform(-margin, WORLD_HEIGHT + margin)
        vel_x = random.uniform(0.2, 1.0)  # Move rightward into screen
        vel_y = random.uniform(-0.5, 0.5)
    else:  # right
        x = WORLD_WIDTH + margin
        y = random.uniform(-margin, WORLD_HEIGHT + margin)
        vel_x = random.uniform(-1.0, -0.2)  # Move leftward into screen
        vel_y = random.uniform(-0.5, 0.5)

    sectorX = x // SECTOR_SIZE
    sectorY = y // SECTOR_SIZE

    asteroid = Asteroid(x, y, vel_x, vel_y, random.uniform(30, 100),
                        (WORLD_WIDTH, WORLD_HEIGHT), (sectorX, sectorY))

    # Add to the existing asteroids dictionary
    if (sectorX, sectorY) in existing_asteroids:
        existing_asteroids[(sectorX, sectorY)].append(asteroid)
    else:
        existing_asteroids[(sectorX, sectorY)] = [asteroid]

    return asteroid  # Return the created asteroid in case you need it
