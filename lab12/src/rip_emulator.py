import json
import random
import ipaddress
from collections import defaultdict
from typing import Dict, List, Tuple

NUM_ROUTERS = 5  


def generate_ip() -> str:
    return str(ipaddress.IPv4Address(random.randint(0x0B000000, 0xDF000000)))  


class Router:
    def __init__(self, ip: str):
        self.ip = ip
        self.neighbors: Dict[str, int] = {}  # IP -> metric
        self.routing_table: Dict[str, Tuple[str, int]] = {}  # dest_ip -> (next_hop, metric)

    def initialize_table(self):
        self.routing_table[self.ip] = (self.ip, 0)
        for neighbor_ip, metric in self.neighbors.items():
            self.routing_table[neighbor_ip] = (neighbor_ip, metric)

    def send_updates(self) -> List[Tuple[str, str, Dict[str, Tuple[str, int]]]]:
        # (куда отправлять, кто отправитель, таблица)
        return [(neighbor, self.ip, self.routing_table.copy()) for neighbor in self.neighbors]

    def receive_update(self, source_ip: str, received_table: Dict[str, Tuple[str, int]]):
        updated = False
        for dest_ip, (next_hop, metric) in received_table.items():
            if dest_ip == self.ip:
                continue
            new_metric = self.neighbors[source_ip] + metric
            if new_metric >= 16:  # RIP max metric
                continue
            if dest_ip not in self.routing_table or new_metric < self.routing_table[dest_ip][1]:
                self.routing_table[dest_ip] = (source_ip, new_metric)
                updated = True
        return updated

    def print_table(self):
        print(f"\nFinal state of router {self.ip} table:")
        print(f"{'Source IP':<16} {'Destination IP':<16} {'Next Hop':<16} {'Metric':<6}")
        for dest_ip, (next_hop, metric) in sorted(self.routing_table.items()):
            print(f"{self.ip:<16} {dest_ip:<16} {next_hop:<16} {metric:<6}")


def create_network_random(num_routers: int) -> Dict[str, Router]:
    routers = {}
    while len(routers) < num_routers:
        ip = generate_ip()
        if ip not in routers:
            routers[ip] = Router(ip)

    router_ips = list(routers.keys())
    for ip in router_ips:
        num_links = random.randint(1, min(3, len(router_ips) - 1))
        neighbors = random.sample([r for r in router_ips if r != ip], num_links)
        for neighbor in neighbors:
            metric = random.randint(1, 5)
            routers[ip].neighbors[neighbor] = metric
            routers[neighbor].neighbors[ip] = metric

    return routers


def run_rip(routers: Dict[str, Router]):
    for router in routers.values():
        router.initialize_table()

    changed = True
    while changed:
        changed = False
        updates = []
        for router in routers.values():
            updates.extend(router.send_updates())

        for target_ip, source_ip, table in updates:
            if target_ip in routers:
                if routers[target_ip].receive_update(source_ip=source_ip, received_table=table):
                    changed = True



def main():
    routers = create_network_random(NUM_ROUTERS)
    run_rip(routers)

    for router in routers.values():
        router.print_table()


if __name__ == "__main__":
    main()
