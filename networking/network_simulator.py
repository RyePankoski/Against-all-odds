from queue import Queue


class NetworkSimulator:
    def __init__(self):
        self.client_to_server_queue = Queue()
        self.server_to_client_queue = Queue()

    def send_to_server(self, message):
        self.client_to_server_queue.put(message)

    def send_to_client(self, message):
        self.server_to_client_queue.put(message)

    def get_server_messages(self):
        messages = []
        while not self.client_to_server_queue.empty():
            messages.append(self.client_to_server_queue.get())
        return messages

    def get_client_messages(self):
        messages = []
        while not self.server_to_client_queue.empty():
            messages.append(self.server_to_client_queue.get())
        return messages

