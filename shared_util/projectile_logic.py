import pygame.draw

from game.settings import *
from shared_util.object_handling import *
import math


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
    # Damage values for different projectile types
    DAMAGE_VALUES = {
        "rocket": 40,
        "bullet": 10
    }

    damage = DAMAGE_VALUES.get(projectile.name, 0)
    ship_collision_radius_squared = (SHIP_HIT_BOX + COLLISION_BUFFER) ** 2

    # Check collisions with ships
    for ship in ships:
        if ship.owner == projectile.owner:
            continue

        if _check_collision(projectile, ship.x, ship.y, ship_collision_radius_squared):
            _apply_ship_damage(ship, damage)
            projectile.alive = False
            return

    # Check collisions with asteroids
    if projectile.sector in asteroids and asteroids[projectile.sector]:
        for asteroid in asteroids[projectile.sector]:
            radius_squared = (asteroid.radius + COLLISION_BUFFER) ** 2

            if _check_collision(projectile, asteroid.x, asteroid.y, radius_squared):
                _apply_asteroid_damage(asteroid, projectile.name, damage)
                projectile.alive = False
                return


def _check_collision(projectile, target_x, target_y, collision_radius_squared):
    """Check both current position and inter-frame collision"""
    distance_squared = (target_x - projectile.x) ** 2 + (target_y - projectile.y) ** 2
    hit_current = distance_squared < collision_radius_squared

    if hit_current:
        return True

    hit_interframe = inter_frame_collision(
        projectile.prev_x, projectile.prev_y,
        projectile.x, projectile.y,
        target_x, target_y,
        collision_radius_squared
    )

    if hit_interframe:
        projectile.x = (projectile.x + projectile.prev_x) / 2
        projectile.y = (projectile.y + projectile.prev_y) / 2
        return True

    return False


def _apply_ship_damage(ship, damage):
    """Apply damage to ship, handling shield mechanics"""
    if ship.shield > 0:
        ship.shield -= damage
        if ship.shield < 0:
            ship.can_shield_recharge = False
            ship.shield = 0
    else:
        ship.health -= damage


def _apply_asteroid_damage(asteroid, projectile_name, damage):
    """Apply damage to asteroid based on projectile type"""
    if projectile_name == "rocket":
        asteroid.alive = False
    else:  # bullet or other projectiles
        asteroid.health -= damage
        if asteroid.health <= 0:
            asteroid.alive = False


def inter_frame_collision(x1, y1, x2, y2, point_x, point_y, collision_distance_squared):
    base_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2

    if base_squared == 0:
        point_distance_squared = (point_x - x1) ** 2 + (point_y - y1) ** 2
        return point_distance_squared <= collision_distance_squared

    t = ((point_x - x1) * (x2 - x1) + (point_y - y1) * (y2 - y1)) / base_squared
    t = max(0, min(1, t))

    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)

    distance_squared = (point_x - closest_x) ** 2 + (point_y - closest_y) ** 2
    return distance_squared <= collision_distance_squared
