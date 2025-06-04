import socket
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
ICMP_CODE = 0

def checksum(source_string):
    countTo = (len(source_string) // 2) * 2
    sum = 0
    count = 0

    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count += 2

    if countTo < len(source_string):
        sum += source_string[-1]
        sum &= 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)

    answer = ~sum & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(id, seq):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, ICMP_CODE, 0, id, seq)
    timestamp = struct.pack('d', time.time())
    dummy_data = b'abcdefghijklmnopqrstuvwabcdefghi'  # 32 байта
    data = timestamp + dummy_data
    packet = header + data
    chksum = checksum(packet)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, ICMP_CODE, socket.htons(chksum), id, seq)
    return header + data

def do_ping(dest_addr, timeout=1, count=4):
    try:
        dest_ip = socket.gethostbyname(dest_addr)
    except socket.gaierror:
        print("Ошибка разрешения адреса")
        return

    print(f"PING {dest_addr} ({dest_ip}): 32 bytes of data.")
    rtts = []
    lost = 0
    icmp_proto = socket.getprotobyname("icmp")
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_proto) as sock:
        pid = os.getpid() & 0xFFFF
        for seq in range(1, count + 1):
            packet = create_packet(pid, seq)
            sock.sendto(packet, (dest_ip, 1))
            start_time = time.time()

            ready = select.select([sock], [], [], timeout)
            if ready[0] == []:
                print("Request timed out.")
                lost += 1
                continue

            recv_packet, addr = sock.recvfrom(1024)
            rcv_time = time.time()

            icmp_header = recv_packet[20:28]
            type, code, checksum, p_id, sequence = struct.unpack("bbHHh", icmp_header)

            if type == 0 and p_id == pid:
                # Echo reply
                bytes_len = len(recv_packet)
                time_sent = struct.unpack("d", recv_packet[28:36])[0]
                rtt = (rcv_time - time_sent) * 1000
                rtts.append(rtt)
                print(f"{bytes_len} bytes from {addr[0]}: icmp_seq={sequence} time={rtt:.2f} ms")
            elif type == 3:
                # Destination unreachable
                error_msg = {
                    0: "Сеть назначения недоступна",
                    1: "Хост назначения недоступен",
                    2: "Протокол недоступен",
                    3: "Порт недоступен",
                    9: "Сеть запрещена администратором",
                    10: "Хост запрещён администратором"
                }.get(code, f"Destination unreachable (code {code})")
                print(f"Ошибка ICMP от {addr[0]}: {error_msg}")
                lost += 1
            else:
                print(f"Получен ICMP-пакет типа {type}, код {code} от {addr[0]}")
                lost += 1

            time.sleep(1)

    print("\n--- {} ping statistics ---".format(dest_addr))
    packets_sent = count
    packets_received = count - lost
    loss = (lost / count) * 100
    print(f"{packets_sent} packets transmitted, {packets_received} received, {loss:.0f}% packet loss")

    if rtts:
        print("rtt min/avg/max = {:.2f}/{:.2f}/{:.2f} ms".format(min(rtts), sum(rtts) / len(rtts), max(rtts)))

if __name__ == "__main__":
    target = input("Введите хост (домен или IP): ")
    do_ping(target)
