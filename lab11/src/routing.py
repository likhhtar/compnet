import threading
from queue import Queue
import time
import copy

INFINITY = float('inf')

class Message:
    def __init__(self, sender_id, vector):
        self.sender_id = sender_id
        self.vector = vector

class Node(threading.Thread):
    def __init__(self, node_id):
        super().__init__()
        self.id = node_id
        self.neighbors = {}  # neighbor_id -> cost
        self.routing_table = {self.id: (0, self.id)}  # destination -> (cost, next_hop)
        self.message_queue = Queue()
        self.neighbor_queues = {}  # neighbor_id -> message_queue
        self.running = True
        self.lock = threading.Lock()

    def add_neighbor(self, neighbor_id, cost, neighbor_queue):
        self.neighbors[neighbor_id] = cost
        self.routing_table[neighbor_id] = (cost, neighbor_id)
        self.neighbor_queues[neighbor_id] = neighbor_queue

    def send_vector_to_neighbors(self):
        vector = self.get_vector()
        for neighbor_id, queue in self.neighbor_queues.items():
            queue.put(Message(self.id, vector))

    def get_vector(self):
        with self.lock:
            return {dst: cost for dst, (cost, _) in self.routing_table.items()}

    def update_routing_table(self, sender_id, sender_vector):
        updated = False
        with self.lock:
            cost_to_sender = self.neighbors[sender_id]
            for dest in sender_vector:
                if dest == self.id:
                    continue
                new_cost = cost_to_sender + sender_vector[dest]
                if (dest not in self.routing_table or
                        new_cost < self.routing_table[dest][0]):
                    self.routing_table[dest] = (new_cost, sender_id)
                    updated = True
        return updated

    def change_link_cost(self, neighbor_id, new_cost):
        with self.lock:
            self.neighbors[neighbor_id] = new_cost
            self.routing_table[neighbor_id] = (new_cost, neighbor_id)
        self.send_vector_to_neighbors()

    def run(self):
        self.send_vector_to_neighbors()
        while self.running:
            try:
                msg = self.message_queue.get(timeout=1)
                if self.update_routing_table(msg.sender_id, msg.vector):
                    self.send_vector_to_neighbors()
            except:
                continue 

    def stop(self):
        self.running = False

    def print_table(self):
        with self.lock:
            print(f"\nNode {self.id} Routing Table:")
            for dst, (cost, nhop) in sorted(self.routing_table.items()):
                print(f"  to {dst}: cost = {cost}, next hop = {nhop}")

def setup_network():
    nodes = {i: Node(i) for i in range(5)}

    links = [
        (0, 1, 1), (1, 2, 1), (0, 3, 2),
        (3, 4, 1), (1, 4, 3)
    ]

    for a, b, cost in links:
        nodes[a].add_neighbor(b, cost, nodes[b].message_queue)
        nodes[b].add_neighbor(a, cost, nodes[a].message_queue)

    for node in nodes.values():
        node.start()

    return nodes

def demonstrate_change(nodes):
    time.sleep(3) 
    print("\n Initial routing tables")
    for node in nodes.values():
        node.print_table()

    print("\n Changing cost between 1 and 4 to 1")
    nodes[1].change_link_cost(4, 1)
    nodes[4].change_link_cost(1, 1)

    time.sleep(3)
    print("\n Updated routing tables")
    for node in nodes.values():
        node.print_table()

    for node in nodes.values():
        node.stop()

if __name__ == "__main__":
    nodes = setup_network()
    demonstrate_change(nodes)
