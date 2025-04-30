import socket
import random
import time
import os

SERVER_ADDR = ('localhost', 9000)
PACKET_LOSS_PROBABILITY = 0.3
UPLOAD_OUTPUT_FILE = 'txt_files/received_from_client.txt'
DOWNLOAD_INPUT_FILE = 'txt_files/file_from_server.txt'
TIMEOUT_SECONDS = 5

def maybe_drop_packet():
    return random.random() < PACKET_LOSS_PROBABILITY

def send_file(sock, addr):
    if not os.path.exists(DOWNLOAD_INPUT_FILE):
        print("[Server] No file to send.")
        return

    with open(DOWNLOAD_INPUT_FILE, 'rb') as f:
        while True:
            chunk = f.read(512)
            if not chunk:
                break

            while True:
                if not maybe_drop_packet():
                    sock.sendto(chunk, addr)
                    print("[Server] Sent chunk.")
                else:
                    print("[Server] Dropped outgoing chunk.")

                try:
                    sock.settimeout(TIMEOUT_SECONDS)
                    ack, _ = sock.recvfrom(1024)
                    if ack == b'ACK':
                        break
                except socket.timeout:
                    print("[Server] Timeout waiting for ACK, resending chunk.")

    sock.sendto(b'EOF', addr)
    print("[Server] Sent EOF.")

def receive_file(sock, data, addr):
    with open(UPLOAD_OUTPUT_FILE, 'ab') as f:  # append mode
        if maybe_drop_packet():
            print("[Server] Dropped incoming packet.")
            return
        if data == b'EOF':
            print("[Server] Received EOF (upload finished).")
        else:
            f.write(data)
            sock.sendto(b'ACK', addr)

def main():
    random.seed(time.time())

    if os.path.exists(UPLOAD_OUTPUT_FILE):
        os.remove(UPLOAD_OUTPUT_FILE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDR)
    print("[Server] Server started at", SERVER_ADDR)

    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue

        if data == b'GET FILE':
            print("[Server] Received GET FILE request.")
            send_file(sock, addr)
        else:
            receive_file(sock, data, addr)

if __name__ == '__main__':
    main()
