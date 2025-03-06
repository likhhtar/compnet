import socket
import sys

def http_client(server_host, server_port, filename):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        request = "GET /{} HTTP/1.1\r\nHost: {}:{}\r\nConnection: close\r\n\r\n".format(filename, server_host, server_port)
        client_socket.sendall(request.encode())

        response = b""
        while True:
            chunk = client_socket.recv(4096)  
            if not chunk:
                break
            response += chunk

        client_socket.close()

        print(response.decode(errors="ignore"))

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <server_host> <server_port> <filename>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filename = sys.argv[3]

    http_client(server_host, server_port, filename)
