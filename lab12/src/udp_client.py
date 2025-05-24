import tkinter as tk
import socket
import threading
import time
import random

SERVER_IP = '127.0.0.1'
PORT = 9999
SEND_INTERVAL = 0.01  # 10ms
PACKET_SIZE = 256

class UDPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP Client")
        self.running = False
        self.packet_id = 0
        self.sent_count = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.start_button = tk.Button(root, text="Start Sending", command=self.start)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status = tk.Label(root, text="Status: Idle")
        self.status.pack()

    def start(self):
        self.running = True
        self.packet_id = 0
        self.sent_count = 0
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.send_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def send_loop(self):
        while self.running:
            timestamp = time.time()
            payload = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=PACKET_SIZE - 20))
            packet = f"{self.packet_id}|{timestamp}|{payload}"
            self.sock.sendto(packet.encode(), (SERVER_IP, PORT))
            self.sent_count += 1
            self.status.config(text=f"Sent: {self.sent_count} packets")
            self.packet_id += 1
            time.sleep(SEND_INTERVAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = UDPClientGUI(root)
    root.mainloop()
