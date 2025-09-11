import socket


class NetworkLayer:
    def __init__(self, bind_socket=False, port=4242, host='localhost'):
        self.socket = None
        self.bind_socket = bind_socket
        self.port = port
        self.host = host

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.bind_socket:
            self.socket.bind((self.host, self.port))
            bound_address = self.socket.getsockname()
            print(f"Server socket bound to {bound_address[0]}:{bound_address[1]}")
        else:
            print("Client socket created (no binding)")

        self.socket.settimeout(0.001)

    def send_to(self, message, address):
        if self.socket:
            self.socket.sendto(message, address)

    def listen_for_messages(self):
        if not self.socket:
            return None
        try:
            data, address = self.socket.recvfrom(1024)
            return data, address
        except socket.timeout:
            return None  # No data available
        except socket.error as e:
            print(f"Socket error: {e}")
            return None
