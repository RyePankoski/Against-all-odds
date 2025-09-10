import pygame.display
from game.settings import *
from lookup_tables import precomputed_angles
import random
from ui_components.button import Button
from entities.ships.ship import Ship
import math
import pygame


def update_ship_facing(ship):
    if ship.dx != 0 or ship.dy != 0:
        angle_rad = math.atan2(-ship.dy, ship.dx)  # -dy because Pygame y increases downward
        ship.facing_angle = math.degrees(angle_rad) - 90  # subtract 90° so "up" is 0°


class MainMenu:
    def __init__(self, screen):
        self.screen = screen

        # All the fancy radar menu stuff.
        self.width, self.height = pygame.display.get_desktop_sizes()[0]
        self.radar_resolution = 360
        self.radar_rays = precomputed_angles.RADAR_DIRECTIONS[self.radar_resolution]
        self.radar_sweep_frames = 1000
        self.current_ray = 0
        self.current_frame = 1
        self.rays_per_frame = self.radar_resolution / self.radar_sweep_frames
        self.can_sweep = True
        self.sweep_timer = 0
        self.sweep_timer_cooldown = 100 / 60
        self.ship_found = False
        self.all_signatures = []
        self.buttons = []
        self.menu_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.init_surface()
        self.init_buttons()

        self.ai_ships = []
        self.init_ai()

        # Set state so game_manager knows to switch
        self.game_state = "menu"

    def run(self, dt, events):
        self.fake_radar_sweep()
        self.render()
        self.handle_buttons(events)
        self.update_ai_ships(dt)

    def handle_buttons(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

        for button in self.buttons:
            button.render()
            clicked = button.update(mouse_pos, mouse_clicked)

            if clicked:
                if button.button_id == "single_player_button":
                    self.game_state = "single_player"
                elif button.button_id == "create_server_button":
                    self.game_state = "create_server"
                elif button.button_id == "join_server_button":
                    self.game_state = "join_server"
                elif button.button_id == "settings_button":
                    self.game_state = "settings"
                elif button.button_id == "credits_button":
                    self.game_state = "credits"
                elif button.button_id == "exit_game_button":
                    pygame.quit()

    def render(self):
        for ship in self.ai_ships:
            if ship.ship_sprite:
                rotated_sprite = pygame.transform.rotate(ship.ship_sprite, ship.facing_angle)
                rect = rotated_sprite.get_rect(center=(int(ship.x), int(ship.y)))
                self.screen.blit(rotated_sprite, rect)
            else:
                pygame.draw.circle(self.menu_surface, RED, (int(ship.x), int(ship.y)), 15)

        for signature in self.all_signatures:
            pygame.draw.circle(self.menu_surface, signature[2], (signature[0], signature[1]), signature[3])

        self.screen.blit(self.menu_surface, (0, 0))

        # Draw sweep line
        if self.current_ray < len(self.radar_rays):
            center_x, center_y = self.width // 2, self.height // 2
            dx, dy = self.radar_rays[self.current_ray]

            # Draw line to edge of radar circle
            line_length = self.height // 2 - 50
            end_x = center_x + dx * line_length
            end_y = center_y + dy * line_length

            pygame.draw.line(self.screen, GREEN, (center_x, center_y), (end_x, end_y), 2)

    def fake_radar_sweep(self):
        signatures = []
        while self.current_ray < self.rays_per_frame * self.current_frame:

            dx, dy = self.radar_rays[self.current_ray]
            self.current_ray += 1
            ray_distance = 0
            ray_x, ray_y = self.width // 2, self.height // 2
            continue_ray = True

            while continue_ray and ray_distance < 160:
                ray_distance += 10
                ray_x += dx * RADAR_PULSE_SPEED
                ray_y += dy * RADAR_PULSE_SPEED

                if random.random() < 0.025:
                    if random.random() < 0.01 and self.ship_found is False:
                        self.ship_found = True
                        signatures.append((ray_x, ray_y, RED, 6))
                    else:
                        signatures.append((ray_x, ray_y, WHITE, 2))
                    continue_ray = False

        if self.current_frame > self.radar_sweep_frames or self.current_ray >= len(self.radar_rays):
            self.init_surface()
            self.ship_found = False
            self.current_frame = 1
            self.current_ray = 0
            self.all_signatures.clear()

        self.current_frame += 1
        self.all_signatures.extend(signatures)

    def update_ai_ships(self, dt):
        ship_speed = 80
        for ship in self.ai_ships:
            update_ship_facing(ship)
            ship.x += ship.dx * dt * ship_speed
            ship.y += ship.dy * dt * ship_speed

            if ship.x < 50 or ship.x > self.width - 50:
                ship.dx *= -1
            if ship.y < 50 or ship.y > self.height - 50:
                ship.dy *= -1

            if random.random() < 0.01:
                ship.dx += random.uniform(-0.5, 0.5)
                ship.dy += random.uniform(-0.5, 0.5)
                # Limit speed
                max_speed = 2
                ship.dx = max(-max_speed, min(max_speed, ship.dx))
                ship.dy = max(-max_speed, min(max_speed, ship.dy))

    def init_surface(self):
        self.menu_surface.fill((0, 0, 0, 0))

        pygame.draw.circle(self.menu_surface, GRAY, (self.width // 2, self.height // 2), self.height // 2 - 30)
        pygame.draw.circle(self.menu_surface, DARK_GREEN, (self.width // 2, self.height // 2), self.height // 2 - 50)
        pygame.draw.circle(self.menu_surface, GRAY, (self.width // 2, self.height // 2), 5)

        title_font = pygame.font.Font("../fonts/title_font2.ttf", 100)
        title_text = "AGAINST ALL ODDS"
        title_surface = title_font.render(title_text, True, GREEN)
        title_rect = title_surface.get_rect()
        title_rect.center = (self.width // 2, 200)

        # Draw background rectangles FIRST
        bg_rect = title_rect.copy()
        bg_rect.inflate_ip(60, 30)
        pygame.draw.rect(self.menu_surface, (20, 20, 20), bg_rect, border_radius=15)  # Dark background
        pygame.draw.rect(self.menu_surface, GREEN, bg_rect, width=3, border_radius=15)  # Green border

        # Then blit the text on top
        self.menu_surface.blit(title_surface, title_rect)

    def init_buttons(self):
        button_width = 700
        button_offset = button_width / 2

        single_player_button = Button(self.width / 2 - button_offset, 300, button_width, 100,
                                      "SINGLE PLAYER | 单人游戏", self.screen, "single_player_button")
        multiplayer_button = Button(self.width / 2 - button_offset, 450, button_width, 100,
                                    "CREATE SERVER | 创建服务器", self.screen, "create_server_button")
        join_server_button = Button(self.width / 2 - button_offset, 600, button_width, 100,
                                    "JOIN SERVER | 加入服务器", self.screen, "join_server_button")
        settings_button = Button(self.width / 2 - button_offset, 750, button_width, 100,
                                 "SETTINGS | 设置", self.screen, "settings_button")
        credits_button = Button(self.width / 2 - button_offset, 900, button_width, 100,
                                "CREDITS | 制作人员", self.screen, "credits_button")
        exit_game_button = Button(self.width / 2 - button_offset, 1050, button_width, 100,
                                  "EXIT GAME | 退出游戏", self.screen, "exit_game_button")

        self.buttons.append(single_player_button)
        self.buttons.append(multiplayer_button)
        self.buttons.append(join_server_button)
        self.buttons.append(settings_button)
        self.buttons.append(credits_button)
        self.buttons.append(exit_game_button)

    def init_ai(self):
        for _ in range(20):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            ship = Ship(x, y, 1, None)  # owner 1, no real player
            ship.dx = random.uniform(-2, 2)
            ship.dy = random.uniform(-2, 2)
            self.ai_ships.append(ship)
