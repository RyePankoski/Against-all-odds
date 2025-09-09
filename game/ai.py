import pygame.draw

from shared_util.ship_logic import *
from ship_subsystems.radar_system import RadarSystem
import random
import math


class AI:
    def __init__(self, ship, player_ship, all_ships, all_asteroids, difficulty, screen, camera):
        self.ship = ship
        self.player_ship = player_ship
        self.all_ships = all_ships
        self.all_asteroids = all_asteroids
        self.difficulty = difficulty
        self.screen = screen
        self.camera = camera

        self.radar = RadarSystem()

        if self.difficulty > 0:
            self.max_bullet_burst = 20
        if self.difficulty > 1:
            self.max_bullet_burst = 30
        if self.difficulty > 2:
            self.max_bullet_burst = 40

        self.detect_player_range_squared = (RADAR_PULSE_RANGE - 300) ** 2
        self.evasive_maneuver_timer = 0
        self.evasive_maneuver_cooldown = 120
        self.can_evasive_maneuver = True

        self.change_wander_timer = 0
        self.change_wander_cooldown = 1000
        self.can_change_wander = True

        self.bullet_burst_timer = 0
        self.bullet_burst_cooldown = 30
        self.can_bullet_burst = True
        self.bullet_burst = 10

        self.is_radar_on = True
        self.can_radar_pulse = True
        self.can_pulse_timer = 0
        self.can_pulse_cooldown = 150 / 60

        self.wander_dx = 0
        self.wander_dy = 0

        self.role = None

    def run(self, dt):
        self.update_counters()
        self.handle_ship(dt)
        self.behaviors()

    def behaviors(self):
        distance_squared = ((self.player_ship.x - self.ship.x) ** 2 +
                            (self.player_ship.y - self.ship.y) ** 2)

        if not (self.detect_player(distance_squared) and self.difficulty > 0):
            self.change_wander()
            self.wander()
            return

        # Movement behavior
        if self.difficulty > 3 and self.ship.shield <= 20:
            self.flee_player(distance_squared)

            if self.difficulty > 4:
                self.parry()

            return

        # 5 difficulty behaviors
        if self.difficulty > 4:
            self.parry()
            self.predator()

        # Combat behavior
        self.move_towards_player(distance_squared)
        self.fire_at_player(distance_squared)

        if self.difficulty > 1:
            self.evasive_maneuver()

        # Aiming behavior
        if self.difficulty > 2:
            self.lead_shots(distance_squared)
        else:
            self.aim_at_player()

    def parry(self):
        if self.ship.can_parry and self.player_ship.firing_a_weapon:
            if random.random() < 0.01:
                self.ship.can_parry = False
                self.ship.is_parrying = True

    def predator(self):
        pass

    def detect_player(self, distance_to_player_squared):
        if distance_to_player_squared < self.detect_player_range_squared:
            return True
        else:
            return False

    def move_towards_player(self, distance_squared):
        self.ship.dampening_active = True
        dx = self.player_ship.x - self.ship.x
        dy = self.player_ship.y - self.ship.y

        if self.difficulty > 3 and self.player_ship.shield < 50:
            stand_off_factor = 120
        else:
            stand_off_factor = 40

        if self.difficulty > 3 and self.ship.shield < 50:
            stand_off_factor = 25

        distance = math.sqrt(distance_squared)
        if distance != 0:
            normalized_dx = dx / distance
            normalized_dy = dy / distance
        else:
            normalized_dx = dx
            normalized_dy = dy

        if distance_squared < self.detect_player_range_squared / stand_off_factor:
            self.ship.dx -= normalized_dx * THRUST
            self.ship.dy -= normalized_dy * THRUST
        else:
            self.ship.dx += normalized_dx * THRUST
            self.ship.dy += normalized_dy * THRUST

    def flee_player(self, distance_squared):
        self.ship.dampening_active = True
        dx = self.player_ship.x - self.ship.x
        dy = self.player_ship.y - self.ship.y

        distance = math.sqrt(distance_squared)

        if distance != 0:
            normalized_dx = dx / distance
            normalized_dy = dy / distance
        else:
            normalized_dx = dx
            normalized_dy = dy

        if distance_squared < self.detect_player_range_squared:
            self.ship.dx -= normalized_dx * THRUST
            self.ship.dy -= normalized_dy * THRUST

        if self.ship.dx != 0 or self.ship.dy != 0:
            look_ahead_distance = 100
            target_x = self.ship.x + self.ship.dx * look_ahead_distance
            target_y = self.ship.y + self.ship.dy * look_ahead_distance
            update_ship_facing(self.ship, (target_x, target_y))

    def aim_at_player(self):
        update_ship_facing(self.ship, (self.player_ship.x, self.player_ship.y))

    def lead_shots(self, distance_squared):
        relative_dx = self.player_ship.dx - self.ship.dx
        relative_dy = self.player_ship.dy - self.ship.dy

        distance = math.sqrt(distance_squared)
        time_to_target = distance / BULLET_SPEED

        lead_x = self.player_ship.x + (relative_dx * time_to_target)
        lead_y = self.player_ship.y + (relative_dy * time_to_target)

        # screen_x, screen_y = self.camera.world_to_screen(lead_x, lead_y)
        # pygame.draw.circle(self.screen, RED, (screen_x, screen_y), 10)

        update_ship_facing(self.ship, (int(lead_x), int(lead_y)))

    def fire_at_player(self, distance_squared):

        rocket_engage_range = self.detect_player_range_squared / 2
        bullet_engage_range = self.detect_player_range_squared / 4

        if distance_squared < rocket_engage_range and self.difficulty > 1:
            if self.ship.can_fire_rocket:
                fire_weapon(self.ship, "rocket")
                self.ship.can_fire_rocket = False

        if distance_squared < bullet_engage_range and self.difficulty > 0:
            if self.ship.can_fire_bullet:
                if self.bullet_burst > 0 and self.can_bullet_burst:
                    self.bullet_burst -= 1
                    if self.bullet_burst <= 0:
                        self.can_bullet_burst = False
                    fire_weapon(self.ship, "bullet")
                    self.ship.can_fire_bullet = False

    def evasive_maneuver(self):
        if not self.can_evasive_maneuver or not self.player_ship.firing_a_weapon:
            return

        if random.random() < 0.3:
            self.can_evasive_maneuver = False

            # Calculate direction TO player
            dx = self.player_ship.x - self.ship.x
            dy = self.player_ship.y - self.ship.y

            length = math.sqrt(dx ** 2 + dy ** 2)
            if length > 0:
                # Normalize direction to player
                dx /= length
                dy /= length

                # True perpendicular (left/right relative to player direction)
                strafe_x = -dy  # Perpendicular to player direction
                strafe_y = dx

                strafe_force = 20
                direction = 1 if random.random() < 0.5 else -1
                self.ship.dx += strafe_x * strafe_force * direction
                self.ship.dy += strafe_y * strafe_force * direction

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
        self.ship.dampening_active = False

        if self.ship.x >= WORLD_WIDTH or self.ship.x <= 0:
            self.can_change_wander = True
            self.can_pulse_timer = 0
        if self.ship.y >= WORLD_HEIGHT or self.ship.y <= 0:
            self.can_change_wander = True
            self.can_pulse_timer = 0

        if self.ship.dx != 0 or self.ship.dy != 0:
            look_ahead_distance = 100
            target_x = self.ship.x + self.ship.dx * look_ahead_distance
            target_y = self.ship.y + self.ship.dy * look_ahead_distance
            update_ship_facing(self.ship, (target_x, target_y))

    def update_counters(self):
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
            self.bullet_burst = random.randint(1, self.max_bullet_burst)

    def radar_system(self):
        if self.is_radar_on:
            if self.ship.can_radar_pulse is True:
                self.radar.begin_scan(self.ship, self.all_ships, self.all_asteroids)
                self.ship.can_radar_pulse = False

        if self.radar.scanning:
            self.radar.continue_scan()

    def handle_ship(self, dt):
        self.ship.run(dt)
        check_ship_collisions(self.ship, self.all_asteroids)

    def get_ai_squad_mates(self):
        squad_mates = []
        for ship in self.all_ships:
            if ship != self.ship and ship.owner == -1:
                squad_mates.append(ship)
        return squad_mates
