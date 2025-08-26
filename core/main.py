import pygame
import sys
from server import Server
from client import Client
from networking.network_simulator import NetworkSimulator

pygame.init()
screen = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0])
clock = pygame.time.Clock()
fake_net = NetworkSimulator()

server = Server(fake_net)
client = Client(1, True, screen, clock, fake_net)

FPS = 60
SERVER_HZ = 20  # Server updates 20 times per second
SERVER_DT = 1 / SERVER_HZ  # Time per server update


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
    return True


def main():
    running = True
    server_timer = 0

    while running:
        screen.fill((0, 0, 0))
        dt = clock.tick(FPS) / 1000
        running = handle_events()
        server_timer += dt
        while server_timer >= SERVER_DT:
            server.run()
            server_timer -= SERVER_DT

        client.run()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
