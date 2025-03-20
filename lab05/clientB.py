import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12345

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        while True:
            command = input("Введите команду для выполнения на сервере ('exit' для выхода): ")
            client_socket.sendall(command.encode())

            if command.lower() == "exit":
                break

            print("\n=== ВЫВОД КОМАНДЫ ===")
            while True:
                output = client_socket.recv(1024).decode()
                if "END_OF_OUTPUT" in output:
                    print(output.replace("END_OF_OUTPUT", "").strip())
                    break
                print(output, end="")

if __name__ == "__main__":
    main()
