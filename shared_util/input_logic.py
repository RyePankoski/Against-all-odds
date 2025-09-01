import pygame
import time


def collect_inputs():
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_screen_pos = pygame.mouse.get_pos()

    input_package = {
        # Movement keys
        'w': keys[pygame.K_w],
        'a': keys[pygame.K_a],
        's': keys[pygame.K_s],
        'd': keys[pygame.K_d],

        # Action keys
        'space': keys[pygame.K_SPACE],  # brake
        'shift': keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],  # boost
        'r': keys[pygame.K_r],  # radar pulse

        # Control panel keys
        'x': keys[pygame.K_x],  # toggle dampening
        'l': keys[pygame.K_l],  # continuous radar

        # Weapon selection
        '1': keys[pygame.K_1],  # missile
        '2': keys[pygame.K_2],  # bullet

        # Mouse input
        'mouse_left': mouse_buttons[0],  # fire weapon
        'mouse_screen_pos': mouse_screen_pos,  # for aiming

        # Timestamp for lag compensation
        'timestamp': time.time()
    }

    return input_package
