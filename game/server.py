from server_scenes.server_main_scene import ServerMainScene
import json
import time


class Server:
    def __init__(self, network_layer):
        self.network_layer = network_layer
        self.sock = None
        self.state = "lobby"
        self.connected_players = {}

        self.message_queue = []
        self.player_names = []

        self.server_main_scene = None

        self.last_heartbeat = time.time()
        self.heartbeat_interval = 1

    def run(self, dt):
        self.listen_for_all_messages()
        self.parse_messages()

        if self.state == "lobby":
            current_time = time.time()

            if current_time - self.last_heartbeat > self.heartbeat_interval:
                self.broadcast_player_ready_status()
                self.last_heartbeat = current_time

                if self.check_if_players_ready():
                    self.server_main_scene = ServerMainScene(self.connected_players)
                    self.state = "in_game"

        if self.state == "in_game":
            self.handle_game(dt)

    def handle_game(self, dt):
        input_messages = []

        for message in self.message_queue:
            if isinstance(message, dict) and 'player_id' in message:
                input_messages.append(message)

        game_state = self.server_main_scene.step(input_messages, dt)

        self.broadcast_game_state(game_state)

    # State management

    def check_if_players_ready(self):
        if not self.connected_players:
            return False

        for address in self.connected_players:
            if not self.connected_players[address]["ready"]:
                return False

        self.broadcast_start_game()
        return True

    # Listen for messages

    def listen_for_all_messages(self):
        # Read ALL available messages, not just one
        while True:
            message = self.network_layer.listen_for_messages()
            if message is not None:
                self.message_queue.append(message)
                print(f"[SERVER] Queued message from {message[1]}")
            else:
                break

    def parse_messages(self):
        for message in self.message_queue:
            if message is not None:
                if self.state == "lobby":
                    self.look_for_connection_attempts(message)
                    self.look_for_ready_up(message)
        self.message_queue = []

    def look_for_connection_attempts(self, message):
        data, address = message
        try:
            data = json.loads(data.decode())
            if data["type"] == "CONNECTION_ATTEMPT":
                player_name = data["player_name"]
                ready = data["ready"]
                return_message = {
                    "type": "CONNECTION_CONFIRMATION",
                    "message": f"Server says Hello to {player_name}",
                    "player_address": str(address),
                }
                return_message = json.dumps(return_message).encode()
                self.network_layer.send_to(return_message, address)
                self.connected_players[address] = {
                    "player_name": player_name,
                    "ready": ready,
                }
        except json.decoder.JSONDecodeError:
            print("[CLIENT] Invalids message format, discarding.")

    def look_for_ready_up(self, message):
        data, address = message
        try:
            data = json.loads(data.decode())
            if data["type"] == "READY":
                print("[SERVER] Saw ready up")
                # Update the player's ready status
                if address in self.connected_players:
                    self.connected_players[address]["ready"] = data["status"]
                    print(f"[SERVER] Player at {address} is now ready: {data['status']}")
                self.broadcast_player_ready_status()
        except json.decoder.JSONDecodeError:
            pass

    def look_for_player_input(self, message):
        """Handle player input during game"""
        data, address = message
        try:
            data = json.loads(data.decode())
            if data["type"] == "PLAYER_INPUT":
                self.message_queue.append({
                    'player_id': address,
                    'input_data': data['input_data'],
                    'timestamp': data.get('timestamp', time.time())
                })
        except json.decoder.JSONDecodeError:
            pass

    # Send messages

    def broadcast_player_ready_status(self):
        player_list = [
            {"name": player["player_name"], "ready": player["ready"]}
            for player in self.connected_players.values()
        ]

        lobby_message = {
            "type": "PLAYERS_STATUS",
            "players": player_list
        }

        message = json.dumps(lobby_message).encode()
        for address in self.connected_players:
            self.network_layer.send_to(message, address)

    def broadcast_start_game(self):
        print("[SERVER] Starting game")

        message = {
            "type": "START_GAME",
            "?": True
        }
        message = json.dumps(message).encode()
        for address in self.connected_players:
            self.network_layer.send_to(message, address)

    def broadcast_game_state(self, game_state):
        state_to_send = {
            'type': 'GAME_UPDATE',
            'ships': [ship.to_dict() for ship in game_state['ships']],
            'projectiles': [proj.to_dict() for proj in game_state['projectiles']],
            'asteroids': {f"{key[0]},{key[1]}": [asteroid.to_dict() for asteroid in value] for key, value in
                          game_state['asteroids'].items()},  # Use this if they're already dicts
            'explosions': game_state['explosions'],
            'timestamp': game_state['timestamp'],
            'collision_events': game_state['collision_events']
        }

        # DEBUG: Print what we're trying to send
        print("Trying to serialize:")
        print(f"Ships: {state_to_send['ships']}")
        print(f"Asteroids: {state_to_send['asteroids']}")
        print(f"Explosions: {state_to_send['explosions']}")

        message = json.dumps(state_to_send).encode()

        for address in self.connected_players:
            self.network_layer.send_to(message, address)
