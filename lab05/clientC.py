import socket

PORT = 12345  
LISTEN_IP = "0.0.0.0"  

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.bind((LISTEN_IP, PORT))  

        print(f"UDP клиент слушает на {LISTEN_IP}:{PORT}")

        while True:
            data, addr = client_socket.recvfrom(1024)  
            print(f"Время от {addr}: {data.decode()}")

if __name__ == "__main__":
    main()
