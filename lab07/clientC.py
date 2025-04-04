import socket
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000
INTERVAL = 1 

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        sequence_number = 1
        print(f"[STARTED] Sending heartbeats to {SERVER_HOST}:{SERVER_PORT}")
        while True:
            timestamp = time.time()
            message = f"{sequence_number} {timestamp:.6f}"
            client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
            print(f"[SENT] seq={sequence_number}")
            sequence_number += 1
            time.sleep(INTERVAL)

if __name__ == "__main__":
    start_client()
