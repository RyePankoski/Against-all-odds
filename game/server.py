import socket


class Server:
    def __init__(self):
        self.sock = None
        self.state = "lobby"
        self.connected_players = []
        self.player_names = []

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 4242))

        print("Socket created!")
        print(f"Socket type: {self.sock.type}")
        print(f"Socket family: {self.sock.family}")

    def run(self, dt):
        print(f"{self.connected_players}")
        if self.state == "lobby":
            self.handle_lobby()

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
            print(f"Got message from {address}: {data}")

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
                self.player_names.append(name)  # Make sure you have this list in __init__

                connection_message = f"Welcome {name}!"
                self.send_to_client(connection_message.encode(), address)
                self.send_to_connected_players()

        except socket.error:
            pass

    def send_to_client(self, message, address):
        self.sock.sendto(message, address)
