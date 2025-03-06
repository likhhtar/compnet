import socket
import sys
import os
import threading
import Queue

def get_file_content(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename, "rb") as f:
            return f.read(), "200 OK"
    return b"404 Not Found", "404 Not Found"

def handle_client(client_socket, client_address):
    try:
        request = client_socket.recv(1024).decode(errors="ignore")
        
        if not request:
            client_socket.close()
            return

        print("Request from {}:\n".format(client_address) + request)

        try:
            requested_file = request.split(" ")[1].strip("/")
            if requested_file == "":
                requested_file = "index.html"
        except IndexError:
            client_socket.close()
            return

        content, status = get_file_content(requested_file)

        response = "HTTP/1.1 {0}\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {1}\r\n\r\n".format(
            status, len(content)
        ).encode() + content

        client_socket.sendall(response)
    except Exception as e:
        print("Error: {}".format(e))
    finally:
        client_socket.close()

def start_server(port, concurrency_level):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    
    print("Server is running on port {} with concurrency level {}...".format(port, concurrency_level))

    thread_pool = Queue.Queue(maxsize=concurrency_level)

    while True:
        client_socket, client_address = server_socket.accept()

        if thread_pool.full():
            print("Server is busy. Waiting for available thread...")
        
        thread_pool.put(1)

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

        client_thread.join()
        thread_pool.get()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python server.py <port> <concurrency_level>")
        sys.exit(1)

    port = int(sys.argv[1])
    concurrency_level = int(sys.argv[2])
    start_server(port, concurrency_level)
