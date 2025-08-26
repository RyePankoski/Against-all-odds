from queue import Queue

import time
import random


class NetworkSimulator:
    def __init__(self):
        self.pending_server_messages = []  # (message, delivery_time)
        self.pending_client_messages = []

        self.delay_low = 0.04
        self.delay_high = 0.08

        # self.delay_low = 2
        # self.delay_high = 4

    def send_to_server(self, message):
        delay = random.uniform(self.delay_low, self.delay_high)  # 20-40ms
        delivery_time = time.time() + delay
        self.pending_server_messages.append((message, delivery_time))

    def get_server_messages(self):
        current_time = time.time()
        ready_messages = []
        still_pending = []

        for message, delivery_time in self.pending_server_messages:
            if current_time >= delivery_time:
                ready_messages.append(message)
            else:
                still_pending.append((message, delivery_time))

        self.pending_server_messages = still_pending
        return ready_messages

    def send_to_client(self, message):
        delay = random.uniform(self.delay_low, self.delay_high)  # 20-40ms
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
