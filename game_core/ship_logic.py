from core.settings import *
import math


def check_ship_collisions(ship, asteroids):
    if ship.sector in asteroids and asteroids[ship.sector]:
        for asteroid in asteroids[ship.sector]:
            distance_squared = (((asteroid.x - ship.x) * (asteroid.x - ship.x)) +
                                ((asteroid.y - ship.y) * (asteroid.y - ship.y)) -
                                (asteroid.radius * asteroid.radius))

            if distance_squared < BULLET_HIT_RANGE * BULLET_HIT_RANGE:
                asteroid.alive = False

                if ship.shield > 0:
                    ship.shield -= 60
                    ship.shield = max(0, ship.shield)

                    if ship.shield == 0:
                        ship.can_recharge = False
                else:
                    ship.health -= 60

                ship.dx *= -0.4
                ship.dy *= -0.4

                return


def update_ship_facing(ship, mouse_world_pos):
    """Update ship facing angle based on mouse world position"""
    import math

    mouse_x, mouse_y = mouse_world_pos

    target_angle = math.degrees(math.atan2(mouse_x - ship.x, mouse_y - ship.y)) + 180
    diff = target_angle - ship.facing_angle

    # Handle angle wrapping
    while diff > 180:
        diff -= 360
    while diff < -180:
        diff += 360

    if abs(diff) <= ROTATION_SPEED:
        ship.facing_angle = target_angle
    else:
        ship.facing_angle += math.copysign(ROTATION_SPEED, diff)


def fire_weapon(ship, weapon_type):
    """Fire weapon based on ship facing angle"""
    import math
    from entities.missile import Missile
    from entities.bullet import Bullet

    if weapon_type == "missile" and ship.missile_ammo <= 0:
        return
    if weapon_type == "bullet" and ship.bullet_ammo <= 0:
        return

    angle = math.radians(ship.facing_angle) + math.pi
    dx = math.sin(angle)
    dy = math.cos(angle)

    true_angle = (dx, dy)
    dx += ship.dx
    dy += ship.dy

    if weapon_type == "missile":
        ship.missile_ammo -= 1
        new_missile = Missile(ship.x, ship.y, dx, dy, ship.facing_angle, ship.owner, true_angle)
        ship.missiles.append(new_missile)
    elif weapon_type == "bullet":
        ship.bullet_ammo -= 1
        new_bullet = Bullet(ship.x, ship.y, dx, dy, ship.facing_angle, ship.owner, true_angle)
        ship.bullets.append(new_bullet)

