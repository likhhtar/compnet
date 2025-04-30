import socket
import time
import threading

HOST = "0.0.0.0"
PORT = 12000
TIMEOUT = 5

# Хранилище для клиентов: { (ip, port): последний_timestamp }
clients = {}

def monitor_clients():
    while True:
        time.sleep(1)
        current_time = time.time()
        for client, last_time in list(clients.items()):
            if current_time - last_time > TIMEOUT:
                print(f"[DISCONNECTED] {client[0]}:{client[1]}")
                del clients[client]

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print(f"[STARTED] Heartbeat server on {HOST}:{PORT}")

        threading.Thread(target=monitor_clients, daemon=True).start()

        while True:
            message, client_address = server_socket.recvfrom(1024)
            timestamp = time.time()

            try:
                decoded = message.decode()
                seq, sent_time = decoded.split()
                sent_time = float(sent_time)
                delta = timestamp - sent_time
                clients[client_address] = timestamp
                print(f"[ALIVE] {client_address[0]}:{client_address[1]} seq={seq} delay={delta:.3f}s")

            except Exception as e:
                print(f"[ERROR] Malformed packet from {client_address}: {e}")

if __name__ == "__main__":
    start_server()
