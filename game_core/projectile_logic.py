from core.settings import *
from game_core.object_handling import *


def handle_missiles(all_missiles, all_ships, all_asteroids, explosion_events):
    missiles_to_remove = []

    for missile in all_missiles:
        missile.handle_self()
        check_missile_collisions(missile, all_ships, all_asteroids)  # Direct call

        if not missile.alive:
            missiles_to_remove.append(missile)
            explosion_events.append((missile.x, missile.y, YELLOW, 100))
            continue

        # Remove missiles that are way outside the world
        if (missile.x < -100 or missile.x > WORLD_WIDTH + 100 or
                missile.y < -100 or missile.y > WORLD_HEIGHT + 100):
            missiles_to_remove.append(missile)

    if missiles_to_remove:
        remove_objects(missiles_to_remove, all_missiles)


def handle_bullets(all_bullets, all_ships, all_asteroids, explosion_events):
    bullets_to_remove = []

    for bullet in all_bullets:
        bullet.handle_self()
        check_bullet_collisions(bullet, all_ships, all_asteroids)  # Direct call

        if not bullet.alive:
            explosion_events.append((bullet.x, bullet.y, CYAN, 10))
            bullets_to_remove.append(bullet)
            continue

        if (bullet.x < -100 or bullet.x > WORLD_WIDTH + 100 or
                bullet.y < -100 or bullet.y > WORLD_HEIGHT + 100):
            bullets_to_remove.append(bullet)

    if bullets_to_remove:
        remove_objects(bullets_to_remove, all_bullets)


def check_missile_collisions(missile, ships, asteroids):  # Renamed from check_bullet_collisions
    for ship in ships:
        if ship.owner == missile.owner:
            continue

        distance_squared = ((ship.x - missile.x) ** 2 +
                            (ship.y - missile.y) ** 2)

        if distance_squared < MISSILE_HIT_RANGE * MISSILE_HIT_RANGE:
            if ship.shield > 0:
                ship.shield -= 40
                if ship.shield < 0:
                    ship.shield = 0

            missile.alive = False
            return

    if missile.sector in asteroids and asteroids[missile.sector]:
        for asteroid in asteroids[missile.sector]:
            distance_squared = (((asteroid.x - missile.x) ** 2 +
                                 (asteroid.y - missile.y) ** 2) -
                                (asteroid.radius * asteroid.radius))

            if distance_squared < MISSILE_HIT_RANGE * MISSILE_HIT_RANGE:
                asteroid.alive = False
                missile.alive = False
                return


def check_bullet_collisions(bullet, ships, asteroids):  # Renamed from check_for_collisions
    for ship in ships:
        if ship.owner == bullet.owner:
            continue

        distance_squared = ((ship.x - bullet.x) ** 2 +
                            (ship.y - bullet.y) ** 2)

        if distance_squared < BULLET_HIT_RANGE * BULLET_HIT_RANGE:
            if ship.shield > 0:
                ship.shield -= 10
                if ship.shield < 0:
                    ship.shield = 0

            bullet.alive = False
            return

    if bullet.sector in asteroids and asteroids[bullet.sector]:
        for asteroid in asteroids[bullet.sector]:
            distance_squared = (((asteroid.x - bullet.x) ** 2 +
                                 (asteroid.y - bullet.y) ** 2) -
                                (asteroid.radius * asteroid.radius))

            if distance_squared < BULLET_HIT_RANGE * BULLET_HIT_RANGE:
                bullet.alive = False
                return
