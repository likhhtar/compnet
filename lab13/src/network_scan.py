from scapy.all import ARP, Ether, srp
from getmac import get_mac_address
import socket
import ipaddress
import os

def get_own_info():
    """Получение информации о собственном компьютере"""
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "127.0.0.1"

    mac = get_mac_address(ip=local_ip)
    try:
        name = socket.gethostbyaddr(local_ip)[0]
    except socket.herror:
        name = hostname
    return {'ip': local_ip, 'mac': mac, 'name': name}


def scan_network(network_cidr):
    """Сканирование подсети"""
    arp = ARP(pdst=network_cidr)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]
    hosts = []
    for sent, received in result:
        try:
            name = socket.gethostbyaddr(received.psrc)[0]
        except socket.herror:
            name = "Unknown"
        hosts.append({
            'ip': received.psrc,
            'mac': received.hwsrc,
            'name': name
        })
    return hosts


def main():
    print("=== Сканирование локальной сети ===\n")
    own = get_own_info()
    print(f"Ваш компьютер: IP={own['ip']}, MAC={own['mac']}, Имя={own['name']}\n")

    # Получение CIDR подсети из IP и маски
    netmask = "255.255.255.0"
    network = ipaddress.IPv4Network(f"{own['ip']}/{netmask}", strict=False)

    print("Найденные компьютеры в сети:\n")
    devices = scan_network(str(network))

    # Поместим собственный ПК в начало, если он в списке
    devices = [d for d in devices if d['ip'] != own['ip']]
    print(f"IP: {own['ip']:<15} MAC: {own['mac']:<17} Имя: {own['name']}")
    for dev in devices:
        print(f"IP: {dev['ip']:<15} MAC: {dev['mac']:<17} Имя: {dev['name']}")


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❗ Запустите программу с правами администратора (sudo)")
    else:
        main()
