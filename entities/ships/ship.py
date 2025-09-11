import random
import pygame
from rendering.sprite_manager import SpriteManager
from shared_util.ship_logic import *


class Ship:
    def __init__(self, x, y, owner, camera):
        self.x = float(x)
        self.y = float(y)
        self.owner = owner
        self.camera = camera

        # Ship movement parameters
        self.dx = 0
        self.dy = 0
        self.facing_angle = 0
        self.sector = 0

        # Projectile stuff
        self.rockets = []
        self.bullets = []
        self.all_projectiles = []

        # State stuff
        self.power = SHIP_POWER
        self.health = SHIP_HEALTH
        self.shield = SHIELD_HEALTH
        self.current_boost_fuel = BOOST_FUEL

        # Weapon handling
        self.firing_a_weapon = False

        self.fire_rocket_timer = 0
        self.fire_rocket_cooldown = 30 / 60
        self.can_fire_rocket = True

        self.fire_bullet_timer = 0
        self.fire_bullet_cooldown = 5 / 60
        self.can_fire_bullet = True

        self.control_panel_timer = 0
        self.control_panel_cooldown = 10 / 60
        self.can_input_controls = True

        self.radar_timer = 0
        self.radar_cooldown = 100 / 60
        self.can_pulse = True

        self.shield_pause_timer = 0
        self.shield_pause_length = 200 / 60
        self.can_shield_recharge = True

        self.bullet_recharge_timer = 0
        self.bullet_recharge_length = 25 / 60
        self.can_reload_bullet = False

        self.rocket_recharge_time = 0
        self.rocket_recharge_length = 300 / 60
        self.can_reload_rocket = False

        self.can_parry_timer = 0
        self.can_parry_timer_cooldown = 180 / 60
        self.can_parry = True

        self.active_parry_timer = 0
        self.active_parry_cooldown = 45 / 60
        self.is_parrying = False

        self.can_radar_pulse = True
        self.can_pulse_timer = 0
        self.can_pulse_cooldown = 150 / 60

        self.radar_signatures = []
        self.radar_resolution_index = 3
        self.available_radar_resolutions = [72, 360, 720, 1440, 3600]
        self.radar_resolution = self.available_radar_resolutions[self.radar_resolution_index]
        self.is_radar_on = True
        self.enemy_radar_ping_coordinates = []

        self.alive = True
        self.dampening_active = True

        screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
        scale_x = screen_width / CAMERA_VIEW_WIDTH
        scale_y = screen_height / CAMERA_VIEW_HEIGHT

        self.ai_ships = ["aiShip", "aiShip2", "aiShip3", "aiShip4"]

        if owner == -1:
            sprite_name = random.choice(self.ai_ships)
        else:
            sprite_name = "ship1"

        # Get original sprite and scale it once
        original_sprite = SpriteManager.get_sprite(sprite_name)
        if original_sprite:
            scaled_width = int(original_sprite.get_width() * scale_x)
            scaled_height = int(original_sprite.get_height() * scale_y)
            self.ship_sprite = pygame.transform.scale(original_sprite, (scaled_width, scaled_height))
        else:
            self.ship_sprite = None

        self.current_weapon = "rocket"
        self.rocket_ammo = MAX_ROCKETS
        self.bullet_ammo = MAX_BULLETS

    def run(self, dt):
        if self.health <= 0:
            self.alive = False
            return
        self.move()
        self.counters(dt)

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
            self.x = WORLD_WIDTH
            self.dx *= -0.5
        elif self.x < 0:
            self.x = 0
            self.dx *= -0.5

        if self.y > WORLD_HEIGHT:
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

    def cycle_radar_resolution(self):
        self.radar_resolution_index += 1
        if self.radar_resolution_index >= len(self.available_radar_resolutions):
            self.radar_resolution_index = 0
        self.radar_resolution = self.available_radar_resolutions[self.radar_resolution_index]

    def counters(self, dt):
        if self.shield < SHIELD_HEALTH and self.can_shield_recharge:
            self.shield += 0.05

        if self.power < SHIP_POWER:
            self.power += 0.04

        if not self.can_fire_rocket:
            self.fire_rocket_timer += dt
            if self.fire_rocket_timer > self.fire_rocket_cooldown:
                self.can_fire_rocket = True
                self.firing_a_weapon = False
                self.fire_rocket_timer = 0
        if not self.can_fire_bullet:
            self.fire_bullet_timer += dt
            if self.fire_bullet_timer > self.fire_bullet_cooldown:
                self.can_fire_bullet = True
                self.firing_a_weapon = False
                self.fire_bullet_timer = 0
        if not self.can_shield_recharge:
            self.shield_pause_timer += dt
            if self.shield_pause_timer > self.shield_pause_length:
                self.can_shield_recharge = True
                self.shield_pause_timer = 0
        if not self.can_reload_rocket:
            self.rocket_recharge_time += dt
            if self.rocket_recharge_time > self.rocket_recharge_length:
                self.can_reload_rocket = True
                self.rocket_recharge_time = 0
        if not self.can_reload_bullet:
            self.bullet_recharge_timer += dt
            if self.bullet_recharge_timer > self.bullet_recharge_length:
                self.can_reload_bullet = True
                self.bullet_recharge_timer = 0
        if not self.can_radar_pulse:
            self.can_pulse_timer += dt
            if self.can_pulse_timer > self.can_pulse_cooldown:
                self.can_radar_pulse = True
                self.can_pulse_timer = 0

        if not self.can_parry:
            self.can_parry_timer += dt
            if self.can_parry_timer > self.can_parry_timer_cooldown:
                self.can_parry = True
                self.can_parry_timer = 0

        if self.is_parrying:
            self.active_parry_timer += dt
            if self.active_parry_timer >= self.active_parry_cooldown:
                self.is_parrying = False
                self.active_parry_timer = 0

        if self.bullet_ammo < MAX_BULLETS and self.can_reload_bullet:
            self.bullet_ammo += 1
            self.can_reload_bullet = False
        if self.rocket_ammo < MAX_ROCKETS and self.can_reload_rocket:
            self.rocket_ammo += 1
            self.can_reload_rocket = False
