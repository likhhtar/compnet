from scapy.all import sniff, IP, TCP, UDP
from collections import defaultdict
import threading

traffic_stats = defaultdict(lambda: {'in': 0, 'out': 0})

import socket

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

local_ip = get_local_ip()


def process_packet(packet):
    if IP in packet:
        ip_layer = packet[IP]
        src = ip_layer.src
        dst = ip_layer.dst
        length = len(packet)

        if TCP in packet or UDP in packet:
            layer = packet[TCP] if TCP in packet else packet[UDP]
            sport = layer.sport
            dport = layer.dport

            # Исходящий трафик
            if src == local_ip:
                traffic_stats[dport]['out'] += length
            # Входящий трафик
            elif dst == local_ip:
                traffic_stats[sport]['in'] += length

def print_report():
    print("\nОтчёт по портам (обновляется каждые 10 секунд):\n")
    while True:
        threading.Event().wait(10)
        print(f"{'Порт':<10} {'Входящий':>12} {'Исходящий':>12}")
        print("-" * 38)
        for port, stats in sorted(traffic_stats.items()):
            print(f"{port:<10} {stats['in']:>12} {stats['out']:>12}")
        print()

def main():
    print("Запуск захвата трафика... ")
    reporter = threading.Thread(target=print_report, daemon=True)
    reporter.start()

    sniff(filter="ip", prn=process_packet, store=False)

if __name__ == "__main__":
    main()
