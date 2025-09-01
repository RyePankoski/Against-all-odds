import pygame
import sys
from server import Server
from game.client import Client
from networking.network_simulator import NetworkSimulator
import cProfile
import pstats

pygame.init()
screen = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
clock = pygame.time.Clock()
fake_net = NetworkSimulator()
connected = True


server = Server(fake_net)
client = Client(screen, clock, fake_net, connected)

FPS = 60
SERVER_HZ = 120
SERVER_DT = 1 / SERVER_HZ


def main():
    running = True
    server_timer = 0

    while running:
        screen.fill((0, 0, 0))
        dt = clock.tick(FPS) / 1000
        server_timer += dt
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False
        if connected:
            # if server_timer >= SERVER_DT:
            server.run(server_timer)
            server_timer = 0

        client.run(dt, events)
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
        stats.print_stats(20)
