from game.settings import *
from shared_util.object_handling import *


def handle_rockets(all_rockets, all_ships, all_asteroids, explosion_events):
    rockets_to_remove = []

    for rocket in all_rockets:
        rocket.update()
        check_projectile_collisions(rocket, all_ships, all_asteroids)  # Direct call

        if not rocket.alive:
            rockets_to_remove.append(rocket)
            explosion_events.append((rocket.x, rocket.y, ORANGE, 150))
            continue

        # Remove rockets that are way outside the world
        if rocket.x < -100 or rocket.x > WORLD_WIDTH + 100 or rocket.y < -100 or rocket.y > WORLD_HEIGHT + 100:
            rockets_to_remove.append(rocket)

    if rockets_to_remove:
        remove_objects(rockets_to_remove, all_rockets)


def handle_bullets(all_bullets, all_ships, all_asteroids, explosion_events):
    bullets_to_remove = []

    for bullet in all_bullets:
        bullet.update()
        check_projectile_collisions(bullet, all_ships, all_asteroids)  # Direct call

        if not bullet.alive:
            explosion_events.append((bullet.x, bullet.y, PALE_BLUE, 50))
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
                if projectile.name == "rocket":
                    ship.shield -= 80
                if projectile.name == "bullet":
                    ship.shield -= 10
                if ship.shield < 0:
                    ship.can_shield_recharge = False
                    ship.shield = 0
                    
            elif ship.shield <= 0:
                if projectile.name == "rocket":
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

                if projectile.name == "rocket":
                    asteroid.alive = False
                    projectile.alive = False
                    return
                if projectile.name == "bullet":
                    asteroid.health -= 10
                    projectile.alive = False

                    if asteroid.health <= 0:
                        asteroid.alive = False
