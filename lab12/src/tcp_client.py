import socket
import threading
import time
import random
import tkinter as tk
from tkinter import ttk

def send_tcp_data(host, port, duration_sec, packet_size, result_callback):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        end_time = time.time() + duration_sec
        total_sent = 0
        packets_sent = 0

        while time.time() < end_time:
            data = bytes(random.getrandbits(8) for _ in range(packet_size))
            client.sendall(data)
            total_sent += len(data)
            packets_sent += 1

        client.close()

        result_callback(total_sent, packets_sent, 0)  # TCP не теряет пакеты
    except Exception as e:
        result_callback(0, 0, 0)
        print(f"[!] Error: {e}")

class TCPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Speed Test Client")

        ttk.Label(root, text="Host:").grid(row=0, column=0)
        self.host_entry = ttk.Entry(root)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1)

        ttk.Label(root, text="Port:").grid(row=1, column=0)
        self.port_entry = ttk.Entry(root)
        self.port_entry.insert(0, "12345")
        self.port_entry.grid(row=1, column=1)

        ttk.Label(root, text="Duration (s):").grid(row=2, column=0)
        self.duration_entry = ttk.Entry(root)
        self.duration_entry.insert(0, "5")
        self.duration_entry.grid(row=2, column=1)

        ttk.Label(root, text="Packet size (bytes):").grid(row=3, column=0)
        self.packet_entry = ttk.Entry(root)
        self.packet_entry.insert(0, "1024")
        self.packet_entry.grid(row=3, column=1)

        self.start_btn = ttk.Button(root, text="Start Test", command=self.start_test)
        self.start_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(root, text="")
        self.result_label.grid(row=5, column=0, columnspan=2)

    def start_test(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        duration = int(self.duration_entry.get())
        packet_size = int(self.packet_entry.get())

        self.result_label.config(text="Testing...")

        thread = threading.Thread(
            target=send_tcp_data,
            args=(host, port, duration, packet_size, self.show_result),
            daemon=True
        )
        thread.start()

    def show_result(self, total_bytes, packets_sent, packets_lost):
        speed_kbps = total_bytes / int(self.duration_entry.get()) / 1024
        self.result_label.config(
            text=f"Sent: {total_bytes} bytes in {self.duration_entry.get()}s\n"
                 f"Speed: {speed_kbps:.2f} KB/s\n"
                 f"Packets sent: {packets_sent}, lost: {packets_lost}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = TCPClientGUI(root)
    root.mainloop()
