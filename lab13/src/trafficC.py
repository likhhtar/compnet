import tkinter as tk
from tkinter import ttk
from scapy.all import sniff, IP, TCP, UDP
import threading

class TrafficMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сетевой монитор")

        self.tree = ttk.Treeview(root, columns=("src", "dst", "proto", "sport", "dport", "len"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.upper())
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Motion>", self.on_hover)

        self.tooltip = tk.Label(root, text="", bg="lightyellow", relief=tk.SOLID, bd=1)
        self.tooltip.place_forget()

        threading.Thread(target=self.sniff_packets, daemon=True).start()

    def sniff_packets(self):
        sniff(prn=self.process_packet, store=False, promisc=True)

    def process_packet(self, pkt):
        if IP in pkt:
            proto = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "IP"
            sport = pkt[TCP].sport if TCP in pkt else pkt[UDP].sport if UDP in pkt else ""
            dport = pkt[TCP].dport if TCP in pkt else pkt[UDP].dport if UDP in pkt else ""
            length = len(pkt)
            row = (pkt[IP].src, pkt[IP].dst, proto, sport, dport, length)
            self.root.after(0, lambda: self.tree.insert("", "end", values=row))

    def on_hover(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            values = self.tree.item(row_id, "values")
            hint_text = f"""
            Протокол: {values[2]}
            IP версия: IPv4
            Отправитель: {values[0]}:{values[3]}
            Получатель: {values[1]}:{values[4]}
            Размер: {values[5]} байт
            """
            self.tooltip.config(text=hint_text.strip())
            self.tooltip.place(x=event.x_root - self.root.winfo_rootx() + 10,
                               y=event.y_root - self.root.winfo_rooty() + 10)
        else:
            self.tooltip.place_forget()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficMonitorApp(root)
    root.mainloop()
