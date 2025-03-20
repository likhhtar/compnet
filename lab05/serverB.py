import socket
import subprocess

HOST = "127.0.0.1"
PORT = 12345

def execute_command(command):
    """Запускает команду и возвращает её вывод"""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        yield line

    for line in process.stderr:
        yield line

    yield "END_OF_OUTPUT\n"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Сервер запущен на {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                print(f"Подключение от {addr}")

                while True:
                    command = client_socket.recv(1024).decode().strip()
                    if not command or command.lower() == "exit":
                        break

                    print(f"Выполнение команды: {command}")

                    for output in execute_command(command):
                        client_socket.sendall(output.encode())

if __name__ == "__main__":
    main()
