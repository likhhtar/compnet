import socket
import random

HOST = "127.0.0.1"  
PORT = 12000       
LOSS_PROBABILITY = 0.2  

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print(f"UDP-сервер запущен на {HOST}:{PORT}")

        while True:
            message, client_address = server_socket.recvfrom(1024)
            print(f"Получено сообщение от {client_address}: {message.decode()}")

            if random.random() < LOSS_PROBABILITY:
                print("Симулируем потерю пакета. Ответ не отправлен.")
                continue

            response = message.decode().upper().encode()
            server_socket.sendto(response, client_address)
            print(f"Отправлен ответ: {response.decode()}")

if __name__ == "__main__":
    start_server()
