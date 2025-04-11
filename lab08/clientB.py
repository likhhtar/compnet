import socket
import random
import time
import os

SERVER_ADDR = ('localhost', 9000)
PACKET_LOSS_PROBABILITY = 0.3
INPUT_FILE = 'txt_files/file_from_client.txt'
RECEIVED_FILE = 'txt_files/received_from_server.txt'
TIMEOUT_SECONDS = 5

def maybe_drop_packet():
    return random.random() < PACKET_LOSS_PROBABILITY

def send_file(sock):
    with open(INPUT_FILE, 'rb') as f:
        while True:
            chunk = f.read(512)
            if not chunk:
                break

            while True:
                if not maybe_drop_packet():
                    sock.sendto(chunk, SERVER_ADDR)
                    print("[Client] Sent chunk.")
                else:
                    print("[Client] Dropped outgoing chunk.")

                try:
                    sock.settimeout(TIMEOUT_SECONDS)
                    ack, _ = sock.recvfrom(1024)
                    if ack == b'ACK':
                        break
                except socket.timeout:
                    print("[Client] Timeout waiting for ACK, resending chunk.")

    sock.sendto(b'EOF', SERVER_ADDR)
    print("[Client] Sent EOF.")

def receive_file(sock):
    # Надёжно отправляем запрос на получение файла
    while True:
        print("[Client] Sending request: GET FILE")
        sock.sendto(b'GET FILE', SERVER_ADDR)
        try:
            sock.settimeout(TIMEOUT_SECONDS)
            data, addr = sock.recvfrom(1024)
            if data:
                break  # Сервер ответил, значит начинаем принимать файл
        except socket.timeout:
            print("[Client] No response, retrying...")

    # Теперь реально принимаем файл
    with open(RECEIVED_FILE, 'wb') as f:
        while True:
            if maybe_drop_packet():
                print("[Client] Dropped incoming packet.")
                continue

            if data == b'EOF':
                print("[Client] Received EOF.")
                break

            f.write(data)
            sock.sendto(b'ACK', addr)
            print("[Client] Sent ACK.")

            try:
                sock.settimeout(TIMEOUT_SECONDS)
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                print("[Client] Timeout waiting for file.")
                break

def main():
    random.seed(time.time())

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    action = input("Choose action (send/receive): ").strip().lower()
    if action == 'send':
        send_file(sock)
    elif action == 'receive':
        receive_file(sock)
    else:
        print("Unknown action.")

    sock.close()

if __name__ == "__main__":
    main()
