import socket
import time
import threading

PORT = 9999
BUFFER_SIZE = 1024

received_packets = {}
start_time = None

def listen_udp():
    global start_time
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    print(f"[+] UDP Server started on port {PORT}")

    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        recv_time = time.time()
        if start_time is None:
            start_time = recv_time

        try:
            parts = data.decode().split('|')
            packet_id = int(parts[0])
            sent_time = float(parts[1])
            received_packets[packet_id] = recv_time - sent_time
        except Exception as e:
            print("Invalid packet:", e)

def report():
    while True:
        time.sleep(2)
        if received_packets:
            duration = time.time() - start_time
            total = len(received_packets)
            loss = max(received_packets.keys()) + 1 - total
            print(f"\n--- UDP Report ---")
            print(f"Duration: {duration:.2f}s")
            print(f"Received packets: {total}")
            print(f"Lost packets: {loss}")
            print(f"Loss rate: {loss / (total + loss) * 100:.2f}%")
            print("------------------\n")

threading.Thread(target=listen_udp, daemon=True).start()
report()
