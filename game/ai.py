import math
import random

from shared_util.ship_logic import *


class AI:
    def __init__(self, ship, player_ship, all_ships, all_asteroids):
        self.ship = ship
        self.player_ship = player_ship
        self.all_ships = all_ships
        self.all_asteroids = all_asteroids
        self.detect_player_range_squared = 3600 ** 2
        # self.detect_player_range_squared = 1000 ** 2

        self.evasive_maneuver_timer = 0
        self.evasive_maneuver_cooldown = 120
        self.can_evasive_maneuver = True

        self.change_wander_timer = 0
        self.change_wander_cooldown = 1000
        self.can_change_wander = True

        self.bullet_burst_timer = 0
        self.bullet_burst_cooldown = 20
        self.can_bullet_burst = True

        self.bullet_burst = 10

        self.wander_dx = 0
        self.wander_dy = 0

    def run(self, dt):

        if not self.can_evasive_maneuver:
            self.evasive_maneuver_timer += 1
            if self.evasive_maneuver_timer >= self.evasive_maneuver_cooldown:
                self.can_evasive_maneuver = True
                self.evasive_maneuver_timer = 0

        if not self.can_change_wander:
            self.change_wander_timer += 1
            if self.change_wander_timer > self.change_wander_cooldown:
                self.can_change_wander = True
                self.change_wander_timer = 0

        if not self.can_bullet_burst:
            self.bullet_burst_timer += 1
            if self.bullet_burst_timer > self.bullet_burst_cooldown:
                self.can_bullet_burst = True
                self.bullet_burst_timer = 0

        if self.bullet_burst <= 0:
            self.bullet_burst = random.randint(1, 30)

        self.ship.update(dt)
        check_ship_collisions(self.ship, self.all_asteroids)

        distance_squared = ((self.player_ship.x - self.ship.x) ** 2 + (self.player_ship.y - self.ship.y) ** 2)

        if self.detect_player(distance_squared):
            self.move_towards_player(distance_squared)
            self.fire_at_player(distance_squared)
            self.evasive_maneuver()
        else:
            self.change_wander()
            self.wander()

    def detect_player(self, distance_to_player_squared):
        if distance_to_player_squared < self.detect_player_range_squared:
            return True
        else:
            return False

    def move_towards_player(self, distance_squared):
        self.ship.dampening_active = True
        update_ship_facing(self.ship, (self.player_ship.x, self.player_ship.y))

        dx = self.player_ship.x - self.ship.x
        dy = self.player_ship.y - self.ship.y

        distance = math.sqrt(distance_squared)

        if distance != 0:
            normalized_dx = dx / distance
            normalized_dy = dy / distance
        else:
            normalized_dx = dx
            normalized_dy = dy

        if distance_squared < self.detect_player_range_squared / 50:
            self.ship.dx -= normalized_dx * THRUST
            self.ship.dy -= normalized_dy * THRUST
        else:
            self.ship.dx += normalized_dx * THRUST
            self.ship.dy += normalized_dy * THRUST

    def fire_at_player(self, distance_squared):

        missile_engage_range = self.detect_player_range_squared/2
        bullet_engage_range = self.detect_player_range_squared/10

        if distance_squared < missile_engage_range:

            if self.ship.can_fire_missile:
                fire_weapon(self.ship, "missile")
                self.ship.can_fire_missile = False
        if distance_squared < bullet_engage_range:
            if self.ship.can_fire_bullet:

                if self.bullet_burst > 0 and self.can_bullet_burst:
                    self.bullet_burst -= 1

                    if self.bullet_burst <= 0:
                        self.can_bullet_burst = False

                    fire_weapon(self.ship, "bullet")
                    self.ship.can_fire_bullet = False

    def evasive_maneuver(self):

        if not self.can_evasive_maneuver:
            return

        if self.player_ship.firing_a_weapon:
            strafe_force = 10

            if random.random() < 0.5:

                self.can_evasive_maneuver = False

                angle = math.radians(self.ship.facing_angle) + math.pi

                dx = math.sin(angle)
                dy = math.cos(angle)

                strafe_right_dx = dy
                strafe_right_dy = -dx

                strafe_left_dx = -dy
                strafe_left_dy = dx

                if random.random() < 0.5:
                    self.ship.dx += strafe_right_dx * strafe_force
                    self.ship.dy += strafe_right_dy * strafe_force
                else:
                    self.ship.dx += strafe_left_dx * strafe_force
                    self.ship.dy += strafe_left_dy * strafe_force

    def change_wander(self):
        if not self.can_change_wander:
            return
        else:
            self.can_change_wander = False

        self.wander_dx = random.uniform(-1, 1)
        self.wander_dy = random.uniform(-1, 1)

        length = math.sqrt(self.wander_dx ** 2 + self.wander_dy ** 2)

        if length > 0:
            self.wander_dx /= length
            self.wander_dy /= length

    def wander(self):
        wander_speed = 10

        self.ship.dx = self.wander_dx * wander_speed
        self.ship.dy = self.wander_dy * wander_speed

        if self.ship.dx != 0 or self.ship.dy != 0:
            look_ahead_distance = 100

            target_x = self.ship.x + self.ship.dx * look_ahead_distance
            target_y = self.ship.y + self.ship.dy * look_ahead_distance

            # Use your existing methods
            update_ship_facing(self.ship, (target_x, target_y))

        self.ship.dampening_active = False
