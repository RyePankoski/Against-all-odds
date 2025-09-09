import time
import random


class NetworkSimulator:
    def __init__(self):
        self.pending_server_messages = []
        self.pending_client_messages = []
        self.chance_to_packet_loss = 0.0001
        self.chance_to_drop_connection = 0.00001

        self.connecting_from = "Austin"

        if self.connecting_from == "Denver":
            self.delay_low = 0.01  # 10ms
            self.delay_high = 0.015  # 15ms
        if self.connecting_from == "Victoria":
            self.delay_low = 0.030  # 30ms
            self.delay_high = 0.036  # 36ms
        if self.connecting_from == "Austin":
            self.delay_low = 0.023  # 35ms
            self.delay_high = 0.03  # 45ms
        if self.connecting_from == "Berlin":
            self.delay_low = 0.121  # 121ms
            self.delay_high = 0.151  # 151ms
        if self.connecting_from == "Tokyo":
            self.delay_low = 0.153  # 153ms
            self.delay_high = 0.200  # 200ms

    def packet_loss(self):
        pass

    def send_to_server(self, message):
        jitter = 0.005
        delay = random.uniform(self.delay_low, self.delay_high)
        delivery_time = time.time() + delay + random.uniform(-jitter, jitter)
        self.pending_server_messages.append((message, delivery_time))

    def get_server_messages(self):
        # Connection drop check (rare)
        if random.random() < self.chance_to_drop_connection:
            self.pending_server_messages = []
            return []

        current_time = time.time()
        ready_messages = []
        still_pending = []

        for message, delivery_time in self.pending_server_messages:
            if random.random() < self.chance_to_packet_loss:
                continue

            if current_time >= delivery_time:
                ready_messages.append(message)
            else:
                still_pending.append((message, delivery_time))

        self.pending_server_messages = still_pending
        return ready_messages

    def send_to_client(self, message):
        delay = random.uniform(self.delay_low, self.delay_high)
        delivery_time = time.time() + delay
        self.pending_client_messages.append((message, delivery_time))

    def get_client_messages(self):
        current_time = time.time()
        ready_messages = []
        still_pending = []

        for message, delivery_time in self.pending_client_messages:
            if current_time >= delivery_time:
                ready_messages.append(message)
            else:
                still_pending.append((message, delivery_time))

        self.pending_client_messages = still_pending
        return ready_messages
