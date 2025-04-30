import socket
import struct
import time
import select
import sys

ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11
ICMP_ECHO_REPLY = 0
MAX_HOPS = 30
TIMEOUT = 2.0

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0

    while count < countTo:
        this_val = (source_string[count + 1]) * 256 + (source_string[count])
        sum = sum + this_val
        sum = sum & 0xffffffff
        count += 2

    if countTo < len(source_string):
        sum += (source_string[len(source_string) - 1])
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    return answer >> 8 | (answer << 8 & 0xff00)

def build_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = struct.pack('d', time.time())
    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), id, 1)
    return header + data

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

def traceroute(dest_name, packets_per_hop=3):
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print("Cannot resolve hostname.")
        return

    print(f"Tracing route to {dest_name} [{dest_addr}]")

    for ttl in range(1, MAX_HOPS + 1):
        print(f"{ttl}", end='\t')
        addresses = []
        times = []

        for attempt in range(packets_per_hop):
            icmp = socket.getprotobyname("icmp")
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            recv_socket.settimeout(TIMEOUT)

            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            recv_socket.bind(("", 0))

            packet_id = int((id(0) * time.time()) % 65535)
            packet = build_packet(packet_id)

            send_time = time.time()
            send_socket.sendto(packet, (dest_addr, 0))

            addr = None
            try:
                ready = select.select([recv_socket], [], [], TIMEOUT)
                if ready[0] == []:
                    print("*", end='\t')
                    continue

                recv_packet, addr = recv_socket.recvfrom(512)
                recv_time = time.time()

                elapsed = round((recv_time - send_time) * 1000, 2)
                times.append(elapsed)

                addresses.append(addr[0])
                print(f"{elapsed} ms", end='\t')
            except socket.timeout:
                print("*", end='\t')
            finally:
                send_socket.close()
                recv_socket.close()

        if addresses:
            ip = addresses[0]
            host = get_hostname(ip)
            if host:
                print(f"{host} [{ip}]")
            else:
                print(f"{ip}")
        else:
            print("Request timed out.")

        if addresses and addresses[0] == dest_addr:
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python traceroute.py <hostname> [packets_per_hop]")
    else:
        host = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        traceroute(host, packets_per_hop=count)
