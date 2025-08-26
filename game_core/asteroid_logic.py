from game_core.object_handling import *
def handle_asteroids(all_asteroids):
    asteroids_to_remove = []
    asteroids_to_relocate = []

    for sector, asteroid_list in all_asteroids.items():
        for asteroid in asteroid_list[:]:
            old_sector = asteroid.sector
            asteroid.float_on()
            new_sector = asteroid.sector

            if not asteroid.alive:
                asteroids_to_remove.append(asteroid)
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