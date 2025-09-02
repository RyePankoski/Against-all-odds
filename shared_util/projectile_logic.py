from game.settings import *
from shared_util.object_handling import *


def handle_missiles(all_missiles, all_ships, all_asteroids, explosion_events):
    missiles_to_remove = []

    for missile in all_missiles:
        missile.update()
        check_projectile_collisions(missile, all_ships, all_asteroids)  # Direct call

        if not missile.alive:
            missiles_to_remove.append(missile)
            explosion_events.append((missile.x, missile.y, YELLOW, 100))
            continue

        # Remove missiles that are way outside the world
        if missile.x < -100 or missile.x > WORLD_WIDTH + 100 or missile.y < -100 or missile.y > WORLD_HEIGHT + 100:
            missiles_to_remove.append(missile)

    if missiles_to_remove:
        remove_objects(missiles_to_remove, all_missiles)


def handle_bullets(all_bullets, all_ships, all_asteroids, explosion_events):
    bullets_to_remove = []

    for bullet in all_bullets:
        bullet.update()
        check_projectile_collisions(bullet, all_ships, all_asteroids)  # Direct call

        if not bullet.alive:
            explosion_events.append((bullet.x, bullet.y, CYAN, 10))
            bullets_to_remove.append(bullet)
            continue

        if bullet.x < -100 or bullet.x > WORLD_WIDTH + 100 or bullet.y < -100 or bullet.y > WORLD_HEIGHT + 100:
            bullets_to_remove.append(bullet)

    if bullets_to_remove:
        remove_objects(bullets_to_remove, all_bullets)


def check_projectile_collisions(projectile, ships, asteroids):
    for ship in ships:
        if ship.owner == projectile.owner:
            continue

        distance_squared = ((ship.x - projectile.x) * (ship.x - projectile.x)
                            + (ship.y - projectile.y) * (ship.y - projectile.y))

        if distance_squared < (SHIP_HIT_BOX + COLLISION_BUFFER) * (SHIP_HIT_BOX + COLLISION_BUFFER):
            if ship.shield > 0:
                if projectile.name == "missile":
                    ship.shield -= 80
                if projectile.name == "bullet":
                    ship.shield -= 10
                if ship.shield < 0:
                    ship.shield = 0
            else:
                if projectile.name == "missile":
                    ship.health -= 80
                if projectile.name == "bullet":
                    ship.health -= 10

            projectile.alive = False
            return

    if projectile.sector in asteroids and asteroids[projectile.sector]:
        for asteroid in asteroids[projectile.sector]:

            distance_squared = (((asteroid.x - projectile.x) * (asteroid.x - projectile.x))
                                + ((asteroid.y - projectile.y) * (asteroid.y - projectile.y)))

            if distance_squared < (asteroid.radius + COLLISION_BUFFER) * (asteroid.radius + COLLISION_BUFFER):

                if projectile.name == "missile":
                    asteroid.alive = False
                    projectile.alive = False
                    return
                if projectile.name == "bullet":
                    asteroid.health -= 10
                    projectile.alive = False

                    if asteroid.health <= 0:
                        asteroid.alive = False
