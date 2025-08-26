import pygame
from core.settings import *
import math
from entities.missile import Missile
from entities.bullet import Bullet
from rendering.sprite_manager import SpriteManager


class Ship:
    def __init__(self, x, y, owner, camera):
        self.x = float(x)
        self.y = float(y)
        self.owner = owner
        self.camera = camera

        self.dx = 0
        self.dy = 0
        self.facing_angle = 0
        self.missiles = []
        self.bullets = []
        self.health = SHIP_HEALTH
        self.shield = SHIELD_HEALTH
        self.sector = 0
        self.current_boost_fuel = BOOST_FUEL

        self.fire_missile_timer = 0
        self.fire_missile_cooldown = 20
        self.can_fire_missile = True

        self.fire_bullet_timer = 0
        self.fire_bullet_cooldown = 2
        self.can_fire_bullet = True

        self.control_panel_timer = 0
        self.control_panel_cooldown = 10
        self.can_input_controls = True

        self.radar_timer = 0
        self.radar_cooldown = 100
        self.can_pulse = True

        self.shield_pause_timer = 0
        self.shield_pause_length = 200
        self.can_recharge = True

        self.bullet_recharge_timer = 0
        self.bullet_recharge_length = 25
        self.can_reload_bullet = False

        self.missile_recharge_time = 0
        self.missile_recharge_length = 300
        self.can_reload_missile = False

        self.alive = True
        self.pulsing = False
        self.dampening_active = True

        self.radar_signatures = []
        self.wants_radar_pulse = False
        self.radar_resolution = 360

        sprite_name = 'ship1' if owner == 1 else 'ship2'
        self.ship_sprite = SpriteManager.get_sprite(sprite_name)
        self.current_weapon = "missile"
        self.missile_ammo = MAX_MISSILES
        self.bullet_ammo = MAX_BULLETS

    def update(self):
        if self.health <= 0:
            self.alive = False
            return

        if self.shield < SHIELD_HEALTH and self.can_recharge:
            self.shield += 0.05

        if self.pulsing:
            self.radar_pulse()

        self.find_angle()
        self.move()

        if self.can_fire_missile is False:
            self.fire_missile_timer += 1
            if self.fire_missile_timer > self.fire_missile_cooldown:
                self.can_fire_missile = True
                self.fire_missile_timer = 0
        if self.can_fire_bullet is False:
            self.fire_bullet_timer += 1
            if self.fire_bullet_timer > self.fire_bullet_cooldown:
                self.can_fire_bullet = True
                self.fire_bullet_timer = 0
        if self.can_input_controls is False:
            self.control_panel_timer += 1
            if self.control_panel_timer > self.control_panel_cooldown:
                self.can_input_controls = True
                self.control_panel_timer = 0
        if self.can_pulse is False:
            self.radar_timer += 1
            if self.radar_timer > self.radar_cooldown:
                self.can_pulse = True
                self.radar_timer = 0
        if self.can_recharge is False:
            self.shield_pause_timer += 1
            if self.shield_pause_timer > self.shield_pause_length:
                self.can_recharge = True
                self.shield_pause_timer = 0
        if self.can_reload_missile is False:
            self.missile_recharge_time += 1
            if self.missile_recharge_time > self.missile_recharge_length:
                self.can_reload_missile = True
                self.missile_recharge_time = 0
        if self.can_reload_bullet is False:
            self.bullet_recharge_timer += 1
            if self.bullet_recharge_timer > self.bullet_recharge_length:
                self.can_reload_bullet = True
                self.bullet_recharge_timer = 0

        if self.bullet_ammo < MAX_BULLETS and self.can_reload_bullet:
            self.bullet_ammo += 1
            self.can_reload_bullet = False
        if self.missile_ammo < MAX_MISSILES and self.can_reload_missile:
            self.missile_ammo += 1
            self.can_reload_missile = False

    def handle_ship_inputs(self, keys, mouse_buttons):
        shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        can_boost = shift_held and self.current_boost_fuel > 0
        current_thrust = BOOST_THRUST if can_boost else THRUST

        if can_boost:
            self.current_boost_fuel -= 1
            self.current_boost_fuel = max(0, min(self.current_boost_fuel, BOOST_FUEL))

        elif not shift_held and self.current_boost_fuel < BOOST_FUEL:
            self.current_boost_fuel += 0.01  # Only regenerate when shift not held at all

        # Movement
        if keys[pygame.K_w]:
            self.dy -= current_thrust
        if keys[pygame.K_a]:
            self.dx -= current_thrust
        if keys[pygame.K_s]:
            self.dy += current_thrust
        if keys[pygame.K_d]:
            self.dx += current_thrust
        if keys[pygame.K_SPACE]:
            self.brake()
        if keys[pygame.K_r]:
            if self.can_pulse:
                self.wants_radar_pulse = True
                self.can_pulse = False

        if keys[pygame.K_1]:
            self.current_weapon = "missile"
        if keys[pygame.K_2]:
            self.current_weapon = "bullet"

        if mouse_buttons[0] and self.can_fire_missile and self.current_weapon == "missile":
            self.fire_missile()
            self.can_fire_missile = False
        if mouse_buttons[0] and self.can_fire_bullet and self.current_weapon == "bullet":
            self.fire_bullet()
            self.can_fire_bullet = False

        self.control_panel(keys)

    def control_panel(self, keys):
        if self.can_input_controls:
            if keys[pygame.K_x]:
                self.dampening_active = not self.dampening_active
                self.can_input_controls = False
            if keys[pygame.K_l]:
                self.pulsing = True
                self.can_input_controls = False

    def radar_pulse(self):
        pass

    def fire_missile(self):
        if self.missile_ammo <= 0:
            return

        self.missile_ammo -= 1

        angle = math.radians(self.facing_angle) + math.pi

        missile_dy = math.cos(angle)
        missile_dx = math.sin(angle)

        true_angle = (missile_dx, missile_dy)
        missile_dx += self.dx
        missile_dy += self.dy

        new_missile = Missile(self.x, self.y, missile_dx, missile_dy, self.facing_angle, self.owner, true_angle)
        self.missiles.append(new_missile)

    def fire_bullet(self):
        if self.bullet_ammo <= 0:
            return

        self.bullet_ammo -= 1

        angle = math.radians(self.facing_angle) + math.pi

        bullet_dy = math.cos(angle)
        bullet_dx = math.sin(angle)

        true_angle = (bullet_dx, bullet_dy)
        bullet_dx += self.dx
        bullet_dy += self.dy

        new_bullet = Bullet(self.x, self.y, bullet_dx, bullet_dy, self.facing_angle, self.owner, true_angle)
        self.bullets.append(new_bullet)

    def move(self):
        self.acceleration()
        self.dampening()
        self.check_bounds()

    def acceleration(self):
        if self.dx == 0 and self.dy == 0:
            return
        else:
            self.x += self.dx
            self.y += self.dy

        sector_x = self.x // SECTOR_SIZE
        sector_y = self.y // SECTOR_SIZE
        self.sector = (sector_x, sector_y)

    def check_bounds(self):
        if self.x > WORLD_WIDTH:
            self.x = WORLD_HEIGHT
            self.dx *= -0.5
        elif self.x < 0:
            self.x = 0
            self.dx *= -0.5

        if self.y > WORLD_WIDTH:
            self.y = WORLD_HEIGHT
            self.dy *= -0.5
        elif self.y < 0:
            self.y = 0
            self.dy *= -0.5

    def brake(self):
        if self.dx < 0:
            self.dx += min(BRAKE, abs(self.dx))
        if self.dx > 0:
            self.dx -= min(BRAKE, abs(self.dx))
        if self.dy > 0:
            self.dy -= min(BRAKE, abs(self.dy))
        if self.dy < 0:
            self.dy += min(BRAKE, abs(self.dy))

    def dampening(self):

        if self.dampening_active:
            if self.dx < 0:
                self.dx += DAMPENING_FORCE
            if self.dx > 0:
                self.dx -= DAMPENING_FORCE
            if self.dy > 0:
                self.dy -= DAMPENING_FORCE
            if self.dy < 0:
                self.dy += DAMPENING_FORCE

    def find_angle(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        world_mouseX, world_mouseY = self.camera.screen_to_world(mouseX, mouseY)

        target_angle = math.degrees(math.atan2(world_mouseX - self.x, world_mouseY - self.y)) + 180
        diff = target_angle - self.facing_angle

        # Handle angle wrapping (now in degrees)
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360

        if abs(diff) <= ROTATION_SPEED:
            self.facing_angle = target_angle
        else:
            self.facing_angle += math.copysign(ROTATION_SPEED, diff)

    def check_for_collisions(self, asteroids):
        if self.sector in asteroids and asteroids[self.sector]:
            for asteroid in asteroids[self.sector]:

                distance_squared = ((((asteroid.x - self.x) * (asteroid.x - self.x)) +
                                     ((asteroid.y - self.y) * (asteroid.y - self.y))) -
                                    (asteroid.radius * asteroid.radius))

                if distance_squared < BULLET_HIT_RANGE * BULLET_HIT_RANGE:
                    asteroid.alive = False

                    if self.shield > 0:
                        self.shield -= 60
                        self.shield = max(0, self.shield)

                        if self.shield == 0:
                            self.can_recharge = False

                    else:
                        self.health -= 60

                    self.dx *= -0.4
                    self.dy *= -0.4

                    return
