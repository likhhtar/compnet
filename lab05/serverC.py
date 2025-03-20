import socket
import time

BROADCAST_IP = "172.20.10.14"  
PORT = 12345 

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
        print(f"UDP сервер вещает на {BROADCAST_IP}:{PORT}")

        while True:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            server_socket.sendto(current_time.encode(), (BROADCAST_IP, PORT))
            time.sleep(1)  

if __name__ == "__main__":
    main()
