import tkinter as tk
import json
from port_forwarder import start_forwarding
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

class PortForwarderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Port Translator")

        self.rules_frame = tk.Frame(root)
        self.rules_frame.pack(pady=10)

        self.refresh_btn = tk.Button(root, text="Refresh Rules", command=self.load_rules)
        self.refresh_btn.pack()

        self.rules_text = tk.Text(self.rules_frame, width=60, height=15)
        self.rules_text.pack()

        self.load_rules()
        start_forwarding()

    def load_rules(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                rules = json.load(f)
            self.rules_text.delete(1.0, tk.END)
            for rule in rules:
                self.rules_text.insert(tk.END, f"Listen: {rule['listen_port']} → {rule['target_ip']}:{rule['target_port']}\n")
        except Exception as e:
            self.rules_text.insert(tk.END, f"Error loading rules: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortForwarderGUI(root)
    root.mainloop()
