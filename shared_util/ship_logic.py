from game.settings import *


def check_ship_collisions(ship, asteroids):
    if ship.sector in asteroids and asteroids[ship.sector]:
        for asteroid in asteroids[ship.sector]:
            distance_squared = (((asteroid.x - ship.x) * (asteroid.x - ship.x)) +
                                ((asteroid.y - ship.y) * (asteroid.y - ship.y)) -
                                (asteroid.radius * asteroid.radius))

            if distance_squared < (asteroid.radius + SHIP_HIT_BOX)**2:
                asteroid.alive = False
                print(f"{ship.owner} hit an asteroid!")

                if ship.shield > 0:
                    ship.shield -= 60
                    ship.shield = max(0, ship.shield)

                    if ship.shield == 0:
                        ship.can_shield_recharge = False
                else:
                    ship.health -= 60

                ship.dx *= -0.5
                ship.dy *= -0.5

                return


def update_ship_facing(ship, mouse_world_pos):
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
    import math
    from entities.rocket import Rocket
    from entities.bullet import Bullet

    if weapon_type == "rocket" and ship.rocket_ammo <= 0:
        return
    if weapon_type == "bullet" and ship.bullet_ammo <= 0:
        return

    angle = math.radians(ship.facing_angle) + math.pi
    dx = math.sin(angle)
    dy = math.cos(angle)

    true_angle = (dx, dy)
    dx += ship.dx
    dy += ship.dy

    if weapon_type == "rocket":
        ship.rocket_ammo -= 1
        new_rocket = Rocket(ship.x, ship.y, dx, dy, ship.facing_angle, ship.owner, true_angle)
        ship.rockets.append(new_rocket)
    elif weapon_type == "bullet":
        ship.bullet_ammo -= 1
        new_bullet = Bullet(ship.x, ship.y, dx, dy, ship.facing_angle, ship.owner, true_angle)
        ship.bullets.append(new_bullet)


def apply_inputs_to_ship(ship, input_data):
    thrust = BOOST_THRUST if input_data.get('shift') and ship.current_boost_fuel > 0 else THRUST

    if input_data.get('w'):
        ship.dy -= thrust
    if input_data.get('a'):
        ship.dx -= thrust
    if input_data.get('s'):
        ship.dy += thrust
    if input_data.get('d'):
        ship.dx += thrust
    if input_data.get('space'):
        ship.brake()

    # Handle boost fuel
    if input_data.get('shift') and ship.current_boost_fuel > 0:
        ship.current_boost_fuel -= 1
        ship.current_boost_fuel = max(0, ship.current_boost_fuel)
    elif not input_data.get('shift') and ship.current_boost_fuel < BOOST_FUEL:
        ship.current_boost_fuel += 0.01

    # Weapon selection (discrete - only on key press)
    if input_data.get('1_pressed'):
        ship.current_weapon = "rocket"
    if input_data.get('2_pressed'):
        ship.current_weapon = "bullet"

    # Firing (continuous - hold to fire)
    if input_data.get('mouse_left'):
        if ship.current_weapon == "rocket" and ship.can_fire_rocket:
            ship.firing_a_weapon = True
            fire_weapon(ship, "rocket")
            ship.can_fire_rocket = False
        elif ship.current_weapon == "bullet" and ship.can_fire_bullet:
            ship.firing_a_weapon = True
            fire_weapon(ship, "bullet")
            ship.can_fire_bullet = False

    # Control panel (discrete - single press toggles)
    if input_data.get('x_pressed'):
        ship.dampening_active = not ship.dampening_active

    if input_data.get('r_pressed'):
        ship.wants_radar_pulse = True
        # No need for can_pulse timer anymore

    # Radar resolution cycling (new discrete input)
    if input_data.get('t_pressed'):
        # You'll need to implement this cycling logic
        ship.cycle_radar_resolution()

    # Update ship facing angle based on mouse position
    if 'mouse_world_pos' in input_data:
        update_ship_facing(ship, input_data['mouse_world_pos'])
