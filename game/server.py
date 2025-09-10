import socket
from server_scenes.server_main_scene import ServerMainScene
import json


class Server:
    def __init__(self):
        self.sock = None
        self.state = "lobby"
        self.connected_players = []
        self.player_names = []
        self.server_main_scene = ServerMainScene()

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 4242))
        print("Socket created!")
        print(f"Socket type: {self.sock.type}")
        print(f"Socket family: {self.sock.family}")

    def run(self, dt):
        if self.state == "lobby":
            self.handle_lobby()
        if self.state == "in_game":
            self._handle_game(dt)

    def _handle_game(self, dt):
        player_inputs = {}
        while True:
            try:
                data, address = self.sock.recvfrom(1024)
                message = json.loads(data.decode())
                player_id = message.get('player_id')
                input_data = message.get('input_data')
                player_inputs[player_id] = input_data
            except socket.error:
                break  # No more messages this frame

        game_state = self.server_main_scene.step(player_inputs, dt)  # step() instead of run()
        self.send_data_to_players(game_state)

    def send_data_to_players(self, game_state):
        for address in self.connected_players:
            self.sock.sendto(json.dumps(game_state).encode(), address)

    def handle_lobby(self):
        self.listen_for_connections()

    def send_to_connected_players(self):
        import json
        player_data = {
            'type': 'player_list',
            'players': self.player_names,
            'count': len(self.connected_players)
        }
        message = json.dumps(player_data).encode()

        for address in self.connected_players:
            print(f"[SERVER] Sending player list to {address}: {self.player_names}")
            self.send_to_client(message, address)

    def listen_for_connections(self):
        try:
            self.sock.settimeout(0)
            data, address = self.sock.recvfrom(1024)
            print(f"[SERVER] Got message from {address}: {data}")

            import json
            try:
                client_data = json.loads(data.decode())
                name = client_data.get('player_name', 'Anonymous')
                print(f"[SERVER] Player connecting: {name}")
            except json.JSONDecodeError:
                # Fallback for non-JSON messages
                name = 'Anonymous'
                print("[SERVER] Couldn't parse JSON, using Anonymous")

            if address not in self.connected_players:
                self.connected_players.append(address)
                self.player_names.append(name)

                connection_message = f"Welcome {name}!"
                self.send_to_client(connection_message.encode(), address)
                self.send_to_connected_players()

        except socket.error:
            pass

    def send_to_client(self, message, address):
        self.sock.sendto(message, address)
