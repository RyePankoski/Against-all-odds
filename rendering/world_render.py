import pygame
from game.settings import *
import math
import random


def generate_star_tiles():
    """Generate pre-rendered star tile surfaces"""
    tiles = []
    MIN_STAR_SIZE = 1
    MAX_STAR_SIZE = 5
    NUM_TILE_VARIATIONS = 10

    for tile_id in range(NUM_TILE_VARIATIONS):
        # Create transparent surface for this tile
        tile_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Use tile_id as seed for consistent patterns
        tile_random = random.Random(tile_id)
        # Draw stars onto this tile surface
        for _ in range(20):
            x = tile_random.randint(0, TILE_SIZE - 1)
            y = tile_random.randint(0, TILE_SIZE - 1)
            size = tile_random.uniform(MIN_STAR_SIZE, MAX_STAR_SIZE)
            pygame.draw.circle(tile_surface, WHITE, (x, y), int(size))
        tiles.append(tile_surface)

    return tiles


class WorldRender:
    def __init__(self, screen):
        self.star_tiles = generate_star_tiles()
        self.screen = screen
        self.font = pygame.font.SysFont('microsoftyahei', 20)

        self.ship_panel_cache = None
        self.last_ship_data = None
        self.text_cache = {}

        screen_width, screen_height = pygame.display.get_desktop_sizes()[0]
        self.scale_x = screen_width / CAMERA_VIEW_WIDTH
        self.scale_y = screen_height / CAMERA_VIEW_HEIGHT

    def _get_cached_text(self, text, color):
        """Cache rendered text surfaces"""
        key = (text, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.font.render(text, True, color)
        return self.text_cache[key]

    def draw_stars_tiled(self, camera, width, height):
        camera_x, camera_y = camera.x, camera.y

        padding = TILE_SIZE * 3
        screen_left = camera_x - width // 2 - padding
        screen_right = camera_x + width // 2 + padding
        screen_top = camera_y - height // 2 - padding
        screen_bottom = camera_y + height // 2 + padding

        start_tile_x = int(screen_left // TILE_SIZE) - 1
        end_tile_x = int(screen_right // TILE_SIZE) + 2
        start_tile_y = int(screen_top // TILE_SIZE) - 1
        end_tile_y = int(screen_bottom // TILE_SIZE) + 2

        for tile_x in range(start_tile_x, end_tile_x):
            for tile_y in range(start_tile_y, end_tile_y):
                tile_index = hash((tile_x, tile_y)) % len(self.star_tiles)
                tile_surface = self.star_tiles[tile_index]

                tile_world_x = tile_x * TILE_SIZE
                tile_world_y = tile_y * TILE_SIZE
                screen_x, screen_y = camera.world_to_screen(tile_world_x, tile_world_y)
                self.screen.blit(tile_surface, (screen_x, screen_y))

    def draw_rockets(self, rockets, camera):
        for rocket in rockets:
            if camera.is_visible(rocket.x, rocket.y):
                screen_x, screen_y = camera.world_to_screen(rocket.x, rocket.y)

                if rocket.scaled_sprite:
                    rotated_sprite = pygame.transform.rotate(rocket.scaled_sprite, rocket.angle)
                    rotated_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
                    self.screen.blit(rotated_sprite, rotated_rect)
                else:
                    # Fallback with scaled radius
                    scaled_radius = int(3 * camera.scale_x)
                    pygame.draw.circle(self.screen, YELLOW, (screen_x, screen_y), scaled_radius)

    def draw_bullets(self, bullets, camera):
        for bullet in bullets:
            if camera.is_visible(bullet.x, bullet.y):
                screen_x, screen_y = camera.world_to_screen(bullet.x, bullet.y)

                if bullet.scaled_sprite:
                    rotated_sprite = pygame.transform.rotate(bullet.scaled_sprite, bullet.angle)
                    rotated_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
                    self.screen.blit(rotated_sprite, rotated_rect)
                else:
                    # Fallback with scaled radius
                    scaled_radius = int(3 * camera.scale_x)
                    pygame.draw.circle(self.screen, YELLOW, (screen_x, screen_y), scaled_radius)

    def draw_ships(self, ships, camera):
        for ship in ships:
            if camera.is_visible(ship.x, ship.y):
                screen_x, screen_y = camera.world_to_screen(ship.x, ship.y)

                if ship.ship_sprite:
                    rotated_sprite = pygame.transform.rotate(ship.ship_sprite, ship.facing_angle)
                    rotated_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
                    self.screen.blit(rotated_sprite, rotated_rect)
                else:
                    # Fallback
                    color = GREEN if ship.owner == 1 else RED
                    pygame.draw.circle(self.screen, color, (screen_x, screen_y), 15)

                shield_surface = pygame.Surface((100, 100), pygame.SRCALPHA)

                # Draw the circle on the alpha surface
                pygame.draw.circle(shield_surface, (173, 216, 230, max(0, ship.shield)), (50, 50), 50 * self.scale_x)

                # Blit the alpha surface to the main screen
                self.screen.blit(shield_surface, (screen_x - 50, screen_y - 50))

    def draw_asteroids(self, asteroid_sectors, camera):
        if not asteroid_sectors:  # Handle empty or None dict
            return

        for asteroid_list in asteroid_sectors.values():
            if not asteroid_list:
                continue

            for asteroid in asteroid_list:
                if asteroid is None:
                    continue

                screen_x, screen_y = camera.world_to_screen(asteroid.x, asteroid.y)

                if 0 <= screen_x <= WORLD_WIDTH and 0 <= screen_y <= WORLD_HEIGHT:
                    pygame.draw.circle(self.screen, DARK_GRAY, (int(screen_x), int(screen_y)), asteroid.radius * self.scale_x)

    def draw_ship_data(self, ship):
        if ship.owner != 1:
            return

        # Create cache key from values that affect the display
        speed = math.sqrt(ship.dx ** 2 + ship.dy ** 2)
        boost_fuel_percent = int((ship.current_boost_fuel / BOOST_FUEL) * 100)
        dampening_active = hasattr(ship, 'dampening_active') and ship.dampening_active

        cache_key = (
            ship.health, int(speed * 10), int(ship.x), int(ship.y),
            boost_fuel_percent, dampening_active, int(ship.shield),
            ship.current_weapon, int(ship.power), ship.radar_resolution,
            ship.rocket_ammo if hasattr(ship, 'rocket_ammo') else 0,
            ship.bullet_ammo if hasattr(ship, 'bullet_ammo') else 0
        )

        # Only re-render if data changed
        if cache_key == self.last_ship_data:
            self.screen.blit(self.ship_panel_cache, (10, 10))
            return

        # Data changed, re-render the panel
        panel_width, panel_height = 250, 300
        panel_surface = pygame.Surface((panel_width, panel_height))

        # Draw panel background
        panel_surface.fill((0, 20, 0))
        pygame.draw.rect(panel_surface, (0, 255, 0), (0, 0, panel_width, panel_height), 2)

        # Colors
        green = (0, 255, 0)
        yellow = (255, 255, 0)
        red = (255, 100, 100)

        dampening_status_en = "ACTIVE 激活" if dampening_active else "OFFLINE 离线"

        if ship.current_weapon == "rocket":
            ammo = f"-rocketS: {ship.rocket_ammo} | 子弹"
        elif ship.current_weapon == "bullet":
            ammo = f"-BULLETS: {ship.bullet_ammo} | 火箭弹"
        else:
            ammo = ""

        data_lines = [
            ("SHIP STATUS | 飞船状态", green, True),  # (text, color, is_title)
            ("", green, False),
            (f"HULL: {ship.health * 10:>3}% | 船体", red if ship.health < 2 else (yellow if ship.health < 5 else green),
             False),
            (f"SPEED: {speed:>5.1f} | 速度", green, False),
            (f"POS X: {int(ship.x):>4} | 位置X", green, False),
            (f"POS Y: {int(ship.y):>4} | 位置Y", green, False),
            (f"BOOST: {boost_fuel_percent:>3}% | 推进",
             red if boost_fuel_percent < 10 else (yellow if boost_fuel_percent < 25 else green), False),
            (f"DAMP: {dampening_status_en:>7}", green if dampening_active else green, False),
            (f"SHIELD: {int(ship.shield):>7}%", green, False),
            (f"WEAPON: {ship.current_weapon:>3} | 武器", green, False),
            (f"RADAR STAT: {int(ship.is_radar_on)} | 电力", green, False),
            (f"RADAR-RES: {ship.radar_resolution} | 分辨率", green, False),
            (ammo, green, False)
        ]

        line_height = 18
        start_y = 15

        for i, (text, color, is_title) in enumerate(data_lines):
            if not text:  # Skip empty lines
                continue

            text_surface = self._get_cached_text(text, color)

            if is_title:
                # Center title
                text_rect = text_surface.get_rect(centerx=panel_width // 2, y=start_y + i * line_height)
            else:
                # Left align data
                text_rect = text_surface.get_rect(x=15, y=start_y + i * line_height)

            panel_surface.blit(text_surface, text_rect)

        # Cache the rendered panel and key
        self.ship_panel_cache = panel_surface
        self.last_ship_data = cache_key

        # Draw to screen
        self.screen.blit(self.ship_panel_cache, (10, 10))

    def draw_radar_screen(self, signatures, enemy_pings, ship_pos, rockets):
        width, height = pygame.display.get_desktop_sizes()[0]

        offset = 300
        radar_screen_size = offset - 50
        radar_screen_position = (width - offset, height - offset)
        radar_rim_size = radar_screen_size + 10

        # Draw radar background
        pygame.draw.circle(self.screen, WHITE, radar_screen_position, radar_rim_size)
        pygame.draw.circle(self.screen, DARK_GREEN, radar_screen_position, radar_screen_size)
        pygame.draw.circle(self.screen, WHITE, radar_screen_position, 5)

        max_radar_range = RADAR_PULSE_RANGE
        radar_scale = radar_screen_size / max_radar_range

        # Inner reference circle
        pygame.draw.circle(self.screen, WHITE, radar_screen_position, (RADAR_PULSE_RANGE * radar_scale) / 2.5, 1)

        # --- Signatures ---
        for sig_x, sig_y, sig_color in signatures:
            relative_x = sig_x - ship_pos[0]
            relative_y = sig_y - ship_pos[1]

            radar_x = relative_x * radar_scale
            radar_y = relative_y * radar_scale

            screen_x = radar_screen_position[0] + radar_x
            screen_y = radar_screen_position[1] + radar_y

            if (radar_x * radar_x + radar_y * radar_y) <= radar_screen_size * radar_screen_size:
                pygame.draw.circle(self.screen, sig_color, (int(screen_x), int(screen_y)), 2)

        # --- Rockets ---
        for rocket in rockets:
            relative_x = rocket.x - ship_pos[0]
            relative_y = rocket.y - ship_pos[1]

            radar_x = relative_x * radar_scale
            radar_y = relative_y * radar_scale

            screen_x = radar_screen_position[0] + radar_x
            screen_y = radar_screen_position[1] + radar_y

            if (radar_x * radar_x + radar_y * radar_y) <= radar_screen_size * radar_screen_size:
                pygame.draw.circle(self.screen, RED, (int(screen_x), int(screen_y)), 1)

        for angle in enemy_pings:
            # Convert angle to unit vector
            dx = -math.cos(angle)  # flip left/right
            dy = math.sin(angle)  # keep up/down the same

            # Scale to radar rim
            edge_x = radar_screen_position[0] + dx * radar_screen_size
            edge_y = radar_screen_position[1] + dy * radar_screen_size

            # Draw a red dot at the edge
            pygame.draw.circle(self.screen, RED, (int(edge_x), int(edge_y)), 10)

    def draw_fps(self, clock):
        fps = f"帧率:{clock.get_fps():.1f}"
        fps_text = self.font.render(fps, True, GREEN)
        self.screen.blit(fps_text, (50, 500))

    def draw_explosions(self, explosions, camera):
        for explosion in explosions:
            if camera.is_visible(explosion[0], explosion[1]):
                screen_x, screen_y = camera.world_to_screen(explosion[0], explosion[1])
                pygame.draw.circle(self.screen, explosion[2], (screen_x, screen_y), explosion[3] * self.scale_x)

    def draw_reticle(self, camera):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Simple crosshair reticle
        line_length = 20
        line_thickness = 2
        color = (0, 255, 0)  # Green

        # Horizontal line
        pygame.draw.line(self.screen, color,
                         (mouse_x - line_length, mouse_y),
                         (mouse_x + line_length, mouse_y), line_thickness)

        # Vertical line
        pygame.draw.line(self.screen, color,
                         (mouse_x, mouse_y - line_length),
                         (mouse_x, mouse_y + line_length), line_thickness)

        # Optional: center dot
        pygame.draw.circle(self.screen, color, (mouse_x, mouse_y), 2)
