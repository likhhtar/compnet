import socket
import threading
import json
import time
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

active_rules = {}
connections = {}

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

def handle_connection(client_sock, target_ip, target_port):
    try:
        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect((target_ip, target_port))

        threading.Thread(target=forward, args=(client_sock, remote_sock), daemon=True).start()
        threading.Thread(target=forward, args=(remote_sock, client_sock), daemon=True).start()
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        client_sock.close()

def start_listener(rule):
    listen_port = rule['listen_port']
    target_ip = rule['target_ip']
    target_port = rule['target_port']

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', listen_port))
    server_sock.listen(5)

    print(f"[+] Listening on port {listen_port} → {target_ip}:{target_port}")
    active_rules[listen_port] = server_sock

    while True:
        try:
            client_sock, addr = server_sock.accept()
            print(f"[+] New connection on {listen_port} from {addr}")
            threading.Thread(target=handle_connection, args=(client_sock, target_ip, target_port), daemon=True).start()
        except:
            break

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load config: {e}")
        return []

def monitor_config():
    last_mtime = 0
    current_rules = {}

    while True:
        try:
            mtime = os.path.getmtime(CONFIG_FILE)
            if mtime != last_mtime:
                last_mtime = mtime
                new_rules = {rule['listen_port']: rule for rule in load_config()}

                for port, rule in new_rules.items():
                    if port not in current_rules:
                        t = threading.Thread(target=start_listener, args=(rule,), daemon=True)
                        t.start()
                current_rules = new_rules
        except Exception as e:
            print(f"[!] Error watching config: {e}")
        time.sleep(1)

def start_forwarding():
    threading.Thread(target=monitor_config, daemon=True).start()
