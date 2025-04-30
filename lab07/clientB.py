import socket
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000
TIMEOUT = 1  # секунд
NUM_PINGS = 10

def ping_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.settimeout(TIMEOUT)

        rtts = []
        lost_packets = 0

        print(f"PING {SERVER_HOST}:{SERVER_PORT}:")

        for seq_num in range(1, NUM_PINGS + 1):
            send_time = time.time()
            message = f"Ping {seq_num} {send_time:.6f}"
            try:
                client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
                response, _ = client_socket.recvfrom(1024)
                recv_time = time.time()

                rtt = (recv_time - send_time) * 1000  # в миллисекундах
                rtts.append(rtt)
                print(f"{len(response)} bytes from {SERVER_HOST}: seq={seq_num} time={rtt:.3f} ms")

            except socket.timeout:
                lost_packets += 1
                print(f"Request timeout for seq={seq_num}")

        print("\n--- Ping statistics ---")
        received_packets = NUM_PINGS - lost_packets
        loss_rate = (lost_packets / NUM_PINGS) * 100

        print(f"{NUM_PINGS} packets transmitted, {received_packets} received, {loss_rate:.0f}% packet loss")

        if rtts:
            min_rtt = min(rtts)
            max_rtt = max(rtts)
            avg_rtt = sum(rtts) / len(rtts)
            print(f"rtt min/avg/max = {min_rtt:.3f}/{avg_rtt:.3f}/{max_rtt:.3f} ms")

if __name__ == "__main__":
    ping_server()
