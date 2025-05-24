import tkinter as tk
from tkinter import ttk, messagebox
from scapy.all import ARP, Ether, srp
from getmac import get_mac_address
import socket
import ipaddress
import threading


def get_own_info():
    """Информация о текущем компьютере"""
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "127.0.0.1"
    mac = get_mac_address(ip=local_ip)
    try:
        name = socket.gethostbyaddr(local_ip)[0]
    except socket.herror:
        name = hostname
    return {'ip': local_ip, 'mac': mac, 'name': name}


class NetworkScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сканер локальной сети")
        self.geometry("600x400")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)

        # Start button
        self.start_button = ttk.Button(self, text="Сканировать сеть", command=self.start_scan)
        self.start_button.pack()

        # Treeview for results
        columns = ("ip", "mac", "name")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("ip", text="IP-адрес")
        self.tree.heading("mac", text="MAC-адрес")
        self.tree.heading("name", text="Имя хоста")
        self.tree.column("ip", width=150)
        self.tree.column("mac", width=180)
        self.tree.column("name", width=220)
        self.tree.pack(padx=10, pady=10, expand=True)

    def start_scan(self):
        self.start_button.config(state="disabled")
        thread = threading.Thread(target=self.scan_network)
        thread.start()

    def scan_network(self):
        self.tree.delete(*self.tree.get_children())
        own = get_own_info()

        netmask = "255.255.255.0"
        network = ipaddress.IPv4Network(f"{own['ip']}/{netmask}", strict=False)
        all_hosts = list(network.hosts())

        self.progress["maximum"] = len(all_hosts)
        self.progress["value"] = 0

        found_devices = []

        for ip in all_hosts:
            ip_str = str(ip)
            # Отправка ARP-запроса
            packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_str)
            result = srp(packet, timeout=1, verbose=0)[0]
            if result:
                _, received = result[0]
                try:
                    hostname = socket.gethostbyaddr(received.psrc)[0]
                except socket.herror:
                    hostname = "Unknown"
                found_devices.append({
                    "ip": received.psrc,
                    "mac": received.hwsrc,
                    "name": hostname
                })

            self.progress["value"] += 1
            self.update_idletasks()

        # Отображение
        self.tree.insert("", "end", values=(own["ip"], own["mac"], own["name"]))
        for dev in found_devices:
            if dev["ip"] != own["ip"]:
                self.tree.insert("", "end", values=(dev["ip"], dev["mac"], dev["name"]))

        self.start_button.config(state="normal")
        messagebox.showinfo("Готово", "Сканирование завершено.")


if __name__ == "__main__":
    app = NetworkScannerGUI()
    app.mainloop()
