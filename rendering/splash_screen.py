import pygame


class SplashScreen:
    def __init__(self, screen, image_path):
        self.screen = screen
        self.alpha = 0
        self.fade_speed = 3
        self.state = "fade_in"
        self.hold_timer = 0
        self.hold_duration = 60

        # Load and scale your image
        try:
            self.splash_image = pygame.image.load(image_path).convert_alpha()
            # Scale to fit screen while maintaining aspect ratio
            screen_rect = screen.get_rect()
            image_rect = self.splash_image.get_rect()

            # Scale image to fit screen
            scale_x = screen_rect.width / image_rect.width
            scale_y = screen_rect.height / image_rect.height
            scale = min(scale_x, scale_y)  # Use smaller scale to fit entirely

            new_width = int(image_rect.width * scale)
            new_height = int(image_rect.height * scale)
            self.splash_image = pygame.transform.scale(self.splash_image, (new_width, new_height))

            # Center the image
            self.image_rect = self.splash_image.get_rect(center=screen_rect.center)

        except pygame.error:
            print(f"Could not load image: {image_path}")
            # Fallback to black screen
            self.splash_image = pygame.Surface(screen.get_size())
            self.splash_image.fill((0, 0, 0))
            self.image_rect = self.splash_image.get_rect()

    def update(self, dt):

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            self.state = "done"

        if self.state == "fade_in":
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = "hold"

        elif self.state == "hold":
            self.hold_timer += 1
            if self.hold_timer >= self.hold_duration:
                self.state = "fade_out"

        elif self.state == "fade_out":
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.state = "done"

    def draw(self):
        # Fill screen with black first
        self.screen.fill((0, 0, 0))

        # Draw image with alpha
        temp_surface = self.splash_image.copy()
        temp_surface.set_alpha(self.alpha)
        self.screen.blit(temp_surface, self.image_rect)

    def is_done(self):
        return self.state == "done"
