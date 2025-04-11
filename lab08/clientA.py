import socket
import random
import time
import os

SERVER_ADDR = ('localhost', 9000)
PACKET_LOSS_PROBABILITY = 0.3
INPUT_FILE = 'txt_files/input.txt'
PACKET_SIZE = 512
TIMEOUT_SECONDS = 2
MAX_RETRIES = 5

def maybe_drop_packet():
    return random.random() < PACKET_LOSS_PROBABILITY

def send_with_retries(sock, packet, addr):
    for attempt in range(MAX_RETRIES):
        if not maybe_drop_packet():
            sock.sendto(packet, addr)
            print(f"[Client] Sent packet (attempt {attempt+1}).")
        else:
            print("[Client] Dropped outgoing packet.")

        try:
            ack, _ = sock.recvfrom(1024)
            if ack == b'ACK':
                print("[Client] Received ACK.")
                return True
        except socket.timeout:
            print("[Client] Timeout waiting for ACK.")

    print("[Client] Failed to send packet after retries.")
    return False

def main():
    random.seed(time.time())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SECONDS)

    if not os.path.exists(INPUT_FILE):
        print(f"[Client] Input file '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, 'rb') as f:
        while True:
            chunk = f.read(PACKET_SIZE)
            if not chunk:
                break
            if not send_with_retries(sock, chunk, SERVER_ADDR):
                print("[Client] Giving up on this packet.")

    send_with_retries(sock, b'EOF', SERVER_ADDR)

    sock.close()
    print("[Client] File sent successfully.")

if __name__ == "__main__":
    main()
