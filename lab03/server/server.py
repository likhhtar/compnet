import socket
import sys
import os

def get_file_content(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename, "rb") as f:
            return f.read(), "200 OK"
    return b"404 Not Found", "404 Not Found"

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(1)
    
    print("Server is running on port " + str(port) + "...")

    while True:
        client_socket, client_address = server_socket.accept()
        request = client_socket.recv(1024).decode()
        
        if not request:
            client_socket.close()
            continue
        
        print("Request: \n" + request)
        print()

        try:
            requested_file = request.split(" ")[1].strip("/")
            if requested_file == "":
                requested_file = "index.html"  
        except IndexError:
            client_socket.close()
            continue

        content, status = get_file_content(requested_file)
        content_type = "text/html" if requested_file.endswith(".html") else "text/plain"
        response = "HTTP/1.1 {0}\r\nContent-Type: {2}; charset=utf-8\r\nContent-Length: {1}\r\n\r\n".format(status, len(content), content_type).encode() + content



        client_socket.sendall(response)
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_server(port)