import socket
import time

def run_server(host='localhost', port=12345):
    print("[*] Starting TCP server...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    print(f"[+] Connection from {addr}")

    start_time = None
    total_bytes = 0

    while True:
        data = conn.recv(4096)
        if not data:
            break
        if start_time is None:
            start_time = time.time()
        total_bytes += len(data)

    end_time = time.time()
    duration = end_time - start_time if start_time else 0

    print(f"[*] Transfer completed.")
    print(f"Total bytes received: {total_bytes}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Speed: {total_bytes / duration / 1024:.2f} KB/s" if duration > 0 else "Duration is zero.")

    conn.close()
    s.close()

if __name__ == "__main__":
    run_server()
