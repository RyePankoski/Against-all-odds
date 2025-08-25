import pygame
from core.settings import *
from rendering.sprite_manager import SpriteManager
import math


def draw_missiles(missiles, camera, screen):
    for missile in missiles:
        if camera.is_visible(missile.x, missile.y):
            screen_x, screen_y = camera.world_to_screen(missile.x, missile.y)

            # Use sprite manager
            rotated_sprite = SpriteManager.get_rotated_sprite('missile', missile.angle)
            if rotated_sprite:
                rotated_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
                screen.blit(rotated_sprite, rotated_rect)
            else:
                # Fallback rendering
                pygame.draw.circle(screen, YELLOW, (screen_x, screen_y), 3)


def draw_bullets(bullets, camera, screen):
    for bullet in bullets:
        if camera.is_visible(bullet.x, bullet.y):
            screen_x, screen_y = camera.world_to_screen(bullet.x, bullet.y)
            pygame.draw.circle(screen, RED, (screen_x, screen_y), 3)


def draw_ships(ships, camera, screen):
    for ship in ships:
        if camera.is_visible(ship.x, ship.y):
            screen_x, screen_y = camera.world_to_screen(ship.x, ship.y)

            if ship.ship_sprite:
                rotated_sprite = pygame.transform.rotate(ship.ship_sprite, ship.facing_angle)
                rotated_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
                screen.blit(rotated_sprite, rotated_rect)
            else:
                # Fallback
                color = GREEN if ship.owner == 1 else RED
                pygame.draw.circle(screen, color, (screen_x, screen_y), 15)

            shield_surface = pygame.Surface((100, 100), pygame.SRCALPHA)

            # Draw the circle on the alpha surface
            pygame.draw.circle(shield_surface, (173, 216, 230, max(0, ship.shield)), (50, 50), 50)

            # Blit the alpha surface to the main screen
            screen.blit(shield_surface, (screen_x - 50, screen_y - 50))


def draw_explosion(screen, camera, x, y):
    screen_x, screen_y = camera.world_to_screen(x, y)
    pygame.draw.circle(screen, YELLOW, (screen_x, screen_y), 50)


def draw_stars(stars, camera, screen, width, height):
    for star in stars:
        screen_x, screen_y = camera.world_to_screen(star[0], star[1])

        # Only draw if visible on screen
        if 0 <= screen_x <= width and 0 <= screen_y <= height:
            pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), int(star[2]))


def draw_asteroids(asteroid_sectors, camera, screen, width, height):
    if not asteroid_sectors:  # Handle empty or None dict
        return

    for asteroid_list in asteroid_sectors.values():
        if not asteroid_list:
            continue

        for asteroid in asteroid_list:
            if asteroid is None:
                continue

            screen_x, screen_y = camera.world_to_screen(asteroid.x, asteroid.y)

            if 0 <= screen_x <= width and 0 <= screen_y <= height:
                pygame.draw.circle(screen, DARK_GRAY, (int(screen_x), int(screen_y)), asteroid.radius)


def draw_ship_data(screen, ship):
    if ship.owner != 1:  # Only show for player 1
        return

    panel_x, panel_y = 10, 10
    panel_width, panel_height = 250, 250

    pygame.draw.rect(screen, (0, 20, 0), (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, (0, 255, 0), (panel_x, panel_y, panel_width, panel_height), 2)

    # CRT-style font
    font = pygame.font.SysFont('microsoftyahei', 20)  # Microsoft YaHei # SimHei (common on Windows)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    red = (255, 100, 100)

    speed = math.sqrt(ship.dx ** 2 + ship.dy ** 2)

    boost_fuel_percent = int((ship.current_boost_fuel / BOOST_FUEL) * 100)

    dampening_status_en = "ACTIVE 激活" if hasattr(ship, 'dampening_active') and ship.dampening_active else "OFFLINE 离线"

    if ship.current_weapon == "missile":
        ammo = f"-MISSILES: {ship.missile_ammo} | 子弹"
    elif ship.current_weapon == "bullet":
        ammo = f"-BULLETS: {ship.bullet_ammo} | 火箭弹"
    else:
        ammo = ""

    shields_level = ship.shield
    shields_level = int(shields_level)
    weapon = ship.current_weapon

    data_lines = [
        f"SHIP STATUS | 飞船状态",
        f"",
        f"HULL: {ship.health * 10:>3}% | 船体",
        f"SPEED: {speed:>5.1f} | 速度",
        f"POS X: {int(ship.x):>4} | 位置X",
        f"POS Y: {int(ship.y):>4} | 位置Y",
        f"BOOST: {boost_fuel_percent:>3}% | 推进",
        f"DAMP: {dampening_status_en:>7}",
        f"SHIELD: {shields_level:>7}%",
        f"WEAPON: {weapon:>3} | 武器",
        ammo
    ]

    # Draw each line
    line_height = 18
    start_y = panel_y + 15

    for i, line in enumerate(data_lines):
        if line == "SHIP STATUS":
            # Title line - centered and bright
            text = font.render(line, True, green)
            text_rect = text.get_rect(centerx=panel_x + panel_width // 2, y=start_y)
        else:
            # Determine color based on content
            color = green  # default
            if "HULL:" in line and ship.health < 5:
                color = red if ship.health < 2 else yellow
            elif "BOOST:" in line and boost_fuel_percent < 25:
                color = red if boost_fuel_percent < 10 else yellow
            elif "DAMP:" in line and dampening_status_en == "ACTIVE":
                color = green

            # Data lines - monospace style
            text = font.render(line, True, color)
            text_rect = text.get_rect(x=panel_x + 15, y=start_y + i * line_height)

        screen.blit(text, text_rect)


def draw_radar_screen(screen, signatures, ship_pos, missiles):
    width, height = pygame.display.get_desktop_sizes()[0]

    offset = 300
    radar_screen_size = offset - 50
    radar_screen_position = (width - offset, height - offset)
    radar_rim_size = radar_screen_size + 10

    # Draw radar background
    pygame.draw.circle(screen, WHITE, radar_screen_position, radar_rim_size)
    pygame.draw.circle(screen, DARK_GREEN, radar_screen_position, radar_screen_size)
    pygame.draw.circle(screen, WHITE, radar_screen_position, 5)

    max_radar_range = RADAR_PULSE_RANGE  # Same as your radar pulse range
    radar_scale = radar_screen_size / max_radar_range

    pygame.draw.circle(screen, WHITE, radar_screen_position, (RADAR_PULSE_RANGE * radar_scale) / 2.5, 1)

    for signature in signatures:
        sig_x = signature[0]
        sig_y = signature[1]

        # Calculate relative position from ship
        relative_x = sig_x - ship_pos[0]
        relative_y = sig_y - ship_pos[1]

        # Scale to radar screen
        radar_x = relative_x * radar_scale
        radar_y = relative_y * radar_scale

        # Position on radar screen (center of radar + relative position)
        screen_x = radar_screen_position[0] + radar_x
        screen_y = radar_screen_position[1] + radar_y

        if (radar_x * radar_x + radar_y * radar_y) <= radar_screen_size * radar_screen_size:
            pygame.draw.circle(screen, signature[2], (int(screen_x), int(screen_y)), 2)

    for missile in missiles:
        x = missile.x
        y = missile.y

        relative_x = x - ship_pos[0]
        relative_y = y - ship_pos[1]

        radar_x = relative_x * radar_scale
        radar_y = relative_y * radar_scale

        screen_x = radar_screen_position[0] + radar_x
        screen_y = radar_screen_position[1] + radar_y

        if (radar_x * radar_x + radar_y * radar_y) <= radar_screen_size * radar_screen_size:
            pygame.draw.circle(screen, RED, (int(screen_x), int(screen_y)), 1)


def draw_fps(screen, clock):
    font = pygame.font.SysFont('microsoftyahei', 20)  # Microsoft YaHei # SimHei (common on Windows)
    fps = f"帧率:{clock.get_fps():.1f}"
    fps_text = font.render(fps, True, GREEN)
    screen.blit(fps_text, (50, 500))
