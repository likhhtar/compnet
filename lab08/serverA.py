import socket
import random
import time
import os

SERVER_ADDR = ('localhost', 9000)
PACKET_LOSS_PROBABILITY = 0.3
OUTPUT_FILE = 'txt_files/received_file.txt'
TIMEOUT_SECONDS = 10

def maybe_drop_packet():
    return random.random() < PACKET_LOSS_PROBABILITY

def main():
    random.seed(time.time())

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDR)
    sock.settimeout(TIMEOUT_SECONDS)

    print(f"[Server] Listening on {SERVER_ADDR}")

    with open(OUTPUT_FILE, 'wb') as f:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                print("[Server] Timeout, closing server.")
                break

            if maybe_drop_packet():
                print("[Server] Dropped incoming packet.")
                continue

            if data == b'EOF':
                print("[Server] Received EOF, finishing.")
                break

            f.write(data)

            # Send ACK
            if not maybe_drop_packet():
                sock.sendto(b'ACK', addr)
                print("[Server] Sent ACK.")
            else:
                print("[Server] Dropped outgoing ACK.")

    sock.close()
    print("[Server] Server shutdown.")

if __name__ == "__main__":
    main()
