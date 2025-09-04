from networking.network_simulator import NetworkSimulator
from game.server import Server
from game.client import Client


class GameManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        connected = True

        fake_net = NetworkSimulator()

        self.server = Server(fake_net)
        self.client = Client(screen, clock, fake_net, connected)

    def run(self, dt, events):

        self.server.run(dt)
        self.client.run(dt, events)



