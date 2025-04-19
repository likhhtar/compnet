import socket
import argparse

def is_port_free(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.bind((ip, port))
        s.close()
        return True
    except socket.error:
        return False

def scan_free_ports(ip, start_port, end_port):
    free_ports = []
    for port in range(start_port, end_port + 1):
        if is_port_free(ip, port):
            free_ports.append(port)
    return free_ports

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display available (free) ports on a given IP address.")
    parser.add_argument("ip", help="IP address to check (e.g., 127.0.0.1)")
    parser.add_argument("start_port", type=int, help="Start of port range")
    parser.add_argument("end_port", type=int, help="End of port range")

    args = parser.parse_args()
    free = scan_free_ports(args.ip, args.start_port, args.end_port)

    if free:
        print("Free ports on {} in range {}-{}:".format(args.ip, args.start_port, args.end_port))
        print(", ".join(str(p) for p in free))
    else:
        print("No free ports found on {} in the specified range.".format(args.ip))
