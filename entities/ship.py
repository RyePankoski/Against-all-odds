from rendering.sprite_manager import SpriteManager
from shared_util.ship_logic import *


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
        self.fire_missile_cooldown = 40 / 60
        self.can_fire_missile = True

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
        self.can_recharge = True

        self.bullet_recharge_timer = 0
        self.bullet_recharge_length = 25 / 60
        self.can_reload_bullet = False

        self.missile_recharge_time = 0
        self.missile_recharge_length = 300 / 60
        self.can_reload_missile = False

        self.alive = True
        self.dampening_active = True

        self.radar_signatures = []
        self.wants_radar_pulse = False
        self.radar_resolution = 1440

        sprite_name = 'ship1' if owner == 1 else 'ship2'
        self.ship_sprite = SpriteManager.get_sprite(sprite_name)
        self.current_weapon = "missile"
        self.missile_ammo = MAX_MISSILES
        self.bullet_ammo = MAX_BULLETS

    def update(self, dt):

        if self.health <= 0:
            self.alive = False
            return

        if self.shield < SHIELD_HEALTH and self.can_recharge:
            self.shield += 0.05

        self.move()

        if self.can_fire_missile is False:
            self.fire_missile_timer += dt
            if self.fire_missile_timer > self.fire_missile_cooldown:
                self.can_fire_missile = True
                self.fire_missile_timer = 0
        if self.can_fire_bullet is False:
            self.fire_bullet_timer += dt
            if self.fire_bullet_timer > self.fire_bullet_cooldown:
                self.can_fire_bullet = True
                self.fire_bullet_timer = 0
        if self.can_input_controls is False:
            self.control_panel_timer += dt
            if self.control_panel_timer > self.control_panel_cooldown:
                self.can_input_controls = True
                self.control_panel_timer = 0
        if self.can_pulse is False:
            self.radar_timer += dt
            if self.radar_timer > self.radar_cooldown:
                self.can_pulse = True
                self.radar_timer = 0
        if self.can_recharge is False:
            self.shield_pause_timer += dt
            if self.shield_pause_timer > self.shield_pause_length:
                self.can_recharge = True
                self.shield_pause_timer = 0
        if self.can_reload_missile is False:
            self.missile_recharge_time += dt
            if self.missile_recharge_time > self.missile_recharge_length:
                self.can_reload_missile = True
                self.missile_recharge_time = 0

        if self.can_reload_bullet is False:
            self.bullet_recharge_timer += dt
            if self.bullet_recharge_timer > self.bullet_recharge_length:
                self.can_reload_bullet = True
                self.bullet_recharge_timer = 0

        if self.bullet_ammo < MAX_BULLETS and self.can_reload_bullet:
            self.bullet_ammo += 1
            self.can_reload_bullet = False
        if self.missile_ammo < MAX_MISSILES and self.can_reload_missile:
            self.missile_ammo += 1
            self.can_reload_missile = False

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
