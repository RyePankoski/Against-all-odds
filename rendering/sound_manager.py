import pygame


class SoundManager:
    def __init__(self):
        self.sounds = {
            'bullet': pygame.mixer.Sound("../resources/sounds/gunfire.mp3"),
            'starting_shot': pygame.mixer.Sound("../resources/sounds/starting_shot.mp3"),
            'rocket': pygame.mixer.Sound("../resources/sounds/rocket.mp3")
        }
        self.gunfire_channel = None
        self.rocket_channel = None
        self.is_shooting = False  # Track shooting state

    def start_gunfire(self):
        if self.gunfire_channel is None or not self.gunfire_channel.get_busy():
            self.gunfire_channel = self.sounds['bullet'].play(loops=-1)

        self.is_shooting = True

    def stop_gunfire_with_fade(self, fade_time_ms=100):
        if self.gunfire_channel and self.gunfire_channel.get_busy():
            self.gunfire_channel.fadeout(fade_time_ms)
            self.gunfire_channel = None
        self.is_shooting = False

    def stop_gunfire(self):
        if self.gunfire_channel and self.gunfire_channel.get_busy():
            self.gunfire_channel.stop()
            self.gunfire_channel = None
        self.is_shooting = False

    def play_rocket_sound(self):
        if self.rocket_channel is None or not self.rocket_channel.get_busy():
            self.rocket_channel = self.sounds['rocket'].play()
