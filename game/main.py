from game.game_manager import GameManager
import cProfile
import pstats
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
clock = pygame.time.Clock()
game_manager = GameManager(screen, clock)
FPS = 60


def main():
    running = True

    while running:
        screen.fill((0, 0, 0))
        dt = clock.tick(FPS) / 1000
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return False

        game_manager.run(dt, events)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    try:
        main()
    finally:
        pr.disable()
        stats = pstats.Stats(pr)
        stats.sort_stats('tottime')
        # stats.print_stats(20)
