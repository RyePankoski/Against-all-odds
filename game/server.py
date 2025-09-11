from server_scenes.server_main_scene import ServerMainScene
import json


class Server:
    def __init__(self, network_layer):
        self.network_layer = network_layer
        self.sock = None
        self.state = "lobby"
        self.connected_players = {}

        self.message_queue = []

        self.player_names = []
        self.server_main_scene = ServerMainScene()

    def run(self, dt):
        self.listen_for_all_messages()

        if self.state == "lobby":
            self._handle_lobby()
        if self.state == "in_game":
            self._handle_game(dt)

    def _handle_lobby(self):
        self.listen_for_connection_attempts()

    def _handle_game(self, dt):
        pass

    def listen_for_all_messages(self):
        message = self.network_layer.listen_for_messages()
        if message is not None:
            self.message_queue.append(message)

    def listen_for_connection_attempts(self):
        for message in self.message_queue:
            if message is not None:
                data, address = message
                try:
                    data = json.loads(data.decode())
                    if data["type"] == "CONNECTION_ATTEMPT":
                        player_name = data["player_name"]
                        return_message = {
                            "type": "CONNECTION_CONFIRMATION",
                            "message": f"Server says Hello to {player_name}"
                        }
                        return_message = json.dumps(return_message).encode()
                        self.network_layer.send_to(return_message, address)
                    else:
                        print("received message, but not a connection attempt")

                except json.decoder.JSONDecodeError:
                    print("[CLIENT] Invalids message format, discarding.")

        self.message_queue = []
