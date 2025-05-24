import socket
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000
TIMEOUT = 1 

def ping_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.settimeout(TIMEOUT)

        for seq_num in range(1, 11):
            send_time = time.time()
            message = f"Ping {seq_num} {send_time:.6f}"

            try:
                client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))

                response, _ = client_socket.recvfrom(1024)
                recv_time = time.time()

                rtt = recv_time - send_time
                print(f"Ответ от сервера: {response.decode()}")
                print(f"RTT: {rtt:.6f} секунд\n")

            except socket.timeout:
                print("Request timed out\n")

if __name__ == "__main__":
    ping_server()
