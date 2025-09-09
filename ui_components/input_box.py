import pygame

from game.settings import *
class InputBox:
    def __init__(self, x, y, width, height, screen):
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = BRIGHT_BLUE
        self.color_active = CYAN
        self.color = self.color_inactive
        self.text = ''
        self.font = pygame.font.Font(None, 24)
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0

    def update(self, dt, events):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # Blink every 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        self.handle_event(events)
        self.draw()

    def handle_event(self, events):

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle active state when clicked
                if self.rect.collidepoint(event.pos):
                    self.active = not self.active
                else:
                    self.active = False
                # Change color based on active state
                self.color = self.color_active if self.active else self.color_inactive

            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        # Return the text when Enter is pressed
                        return self.text
                    elif event.key == pygame.K_BACKSPACE:
                        if self.cursor_pos > 0:
                            self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                            self.cursor_pos -= 1
                    elif event.key == pygame.K_DELETE:
                        if self.cursor_pos < len(self.text):
                            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                    elif event.key == pygame.K_LEFT:
                        self.cursor_pos = max(0, self.cursor_pos - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                    elif event.key == pygame.K_HOME:
                        self.cursor_pos = 0
                    elif event.key == pygame.K_END:
                        self.cursor_pos = len(self.text)
                    else:
                        # Add character at cursor position
                        char = event.unicode
                        if char.isprintable():
                            self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                            self.cursor_pos += 1

                    # Re-render the text
                    self.txt_surface = self.font.render(self.text, True, pygame.Color('black'))

            return None

    def draw(self):
        # Draw the input box rectangle
        pygame.draw.rect(self.screen, pygame.Color('white'), self.rect)
        pygame.draw.rect(self.screen, self.color, self.rect, 2)

        # Draw the text
        self.screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # Draw cursor if active and visible
        if self.active and self.cursor_visible:
            # Calculate cursor x position
            text_before_cursor = self.text[:self.cursor_pos]
            cursor_x = self.rect.x + 5 + self.font.size(text_before_cursor)[0]
            cursor_y = self.rect.y + 5
            cursor_height = self.font.get_height()
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 1)

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.cursor_pos = len(text)
        self.txt_surface = self.font.render(self.text, True, pygame.Color('black'))

    def clear(self):
        self.text = ''
        self.cursor_pos = 0
        self.txt_surface = self.font.render(self.text, True, pygame.Color('black'))
