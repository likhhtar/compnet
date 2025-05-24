import threading
import socket
import json
import random
import time
from typing import Dict, Tuple, List

NUM_ROUTERS = 5
BASE_PORT = 5000


class RouterThread(threading.Thread):
    def __init__(self, name, port, neighbors):
        super().__init__()
        self.name = name
        self.port = port
        self.neighbors: Dict[str, Tuple[int, int]] = neighbors  # name -> (port, metric)
        self.routing_table: Dict[str, Tuple[str, int]] = {self.name: (self.name, 0)}
        self.updated = True
        self.lock = threading.Lock()

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', self.port))
        server.listen()

        while True:
            if self.updated:
                self.updated = False
                self.send_table_to_neighbors()

            server.settimeout(1.0)
            try:
                conn, _ = server.accept()
                data = conn.recv(4096)
                conn.close()
                if data:
                    received = json.loads(data.decode())
                    self.process_update(received['from'], received['table'])
            except socket.timeout:
                continue

    def send_table_to_neighbors(self):
        for neighbor_name, (neighbor_port, _) in self.neighbors.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', neighbor_port))
                message = json.dumps({
                    'from': self.name,
                    'table': self.routing_table
                })
                s.send(message.encode())
                s.close()
            except ConnectionRefusedError:
                continue

    def process_update(self, from_router, table):
        updated = False
        cost_to_sender = self.neighbors.get(from_router, (None, 16))[1]

        for dest, (next_hop, metric) in table.items():
            new_metric = min(16, metric + cost_to_sender)
            if dest == self.name or new_metric >= 16:
                continue
            if dest not in self.routing_table or new_metric < self.routing_table[dest][1]:
                with self.lock:
                    self.routing_table[dest] = (from_router, new_metric)
                updated = True

        if updated:
            self.updated = True

    def print_table(self):
        print(f"\nFinal routing table for {self.name} (port {self.port})")
        print(f"{'Source':<10} {'Destination':<15} {'Next Hop':<10} {'Metric':<6}")
        for dest, (next_hop, metric) in sorted(self.routing_table.items()):
            print(f"{self.name:<10} {dest:<15} {next_hop:<10} {metric:<6}")


def generate_network(num_routers: int) -> Dict[str, RouterThread]:
    routers = {}
    ports = [BASE_PORT + i for i in range(num_routers)]

    # Step 1: Create routers
    for i in range(num_routers):
        name = f'R{i}'
        routers[name] = {
            'port': ports[i],
            'neighbors': {}
        }

    # Step 2: Randomly connect routers
    names = list(routers.keys())
    for name in names:
        other_names = [n for n in names if n != name]
        num_links = random.randint(1, min(3, len(other_names)))
        connections = random.sample(other_names, num_links)
        for neighbor in connections:
            metric = random.randint(1, 5)
            routers[name]['neighbors'][neighbor] = (routers[neighbor]['port'], metric)
            routers[neighbor]['neighbors'][name] = (routers[name]['port'], metric)

    # Step 3: Instantiate RouterThreads
    threads = {}
    for name, config in routers.items():
        threads[name] = RouterThread(name, config['port'], config['neighbors'])

    return threads


def main():
    routers = generate_network(NUM_ROUTERS)

    # Start all router threads
    for router in routers.values():
        router.start()

    print("[*] RIP simulation started with threads + sockets...\n")

    time.sleep(10)

    for router in routers.values():
        router.print_table()


if __name__ == "__main__":
    main()
