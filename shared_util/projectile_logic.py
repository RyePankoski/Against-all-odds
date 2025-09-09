from game.settings import *
from shared_util.object_handling import *
from entities.ships.battleship import BattleShip
from entities.projectiles.rocket import Rocket
from entities.projectiles.bullet import Bullet


def handle_projectile(all_projectiles, all_ships, all_asteroids, explosion_events):
    projectiles_to_remove = []

    for projectile in all_projectiles:
        projectile.run()
        check_projectile_collisions(projectile, all_ships, all_asteroids)

        if not projectile.alive:
            projectiles_to_remove.append(projectile)

            if isinstance(projectile, Rocket):
                explosion_events.append((projectile.x, projectile.y, ORANGE, 150))
            elif isinstance(projectile, Bullet):
                explosion_events.append((projectile.x, projectile.y, CYAN, 50))

        if projectile.x < -100 or projectile.x > WORLD_WIDTH + 100 or projectile.y < -100 or projectile.y > WORLD_HEIGHT + 100:
            projectiles_to_remove.append(projectile)

    remove_objects(projectiles_to_remove, all_projectiles)


def check_projectile_collisions(projectile, ships, asteroids):
    # Damage values for different projectile types
    DAMAGE_VALUES = {
        "rocket": 40,
        "bullet": 20
    }

    damage = DAMAGE_VALUES.get(projectile.name, 0)
    parry_collision_radius_squared = (PARRY_RANGE + COLLISION_BUFFER) ** 2

    # Check collisions with ships
    for ship in ships:
        if ship.owner == projectile.owner:
            continue

        if isinstance(ship, BattleShip):
            ship_collision_radius_squared = (BS_HIT_BOX + COLLISION_BUFFER) ** 2
        else:
            ship_collision_radius_squared = (SHIP_HIT_BOX + COLLISION_BUFFER) ** 2

        if hasattr(ship, 'is_parrying'):
            if ship.is_parrying:
                if _check_collision(projectile, ship.x, ship.y, parry_collision_radius_squared):
                    projectile.true_dx *= -1
                    projectile.true_dy *= -1
                    projectile.dx *= -1
                    projectile.dy *= -1
                    projectile.owner = ship.owner
                    return

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
