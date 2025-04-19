import socket
import psutil

def get_ip_and_netmask():
    addrs = psutil.net_if_addrs()
    for iface_name, iface_addrs in addrs.items():
        for addr in iface_addrs:
            if addr.family == socket.AF_INET:
                print("Interface: ", iface_name)
                print("IP-address: ", addr.address)
                print("Netmask: ",addr.netmask)
                print("-" * 30)

if __name__ == "__main__":
    get_ip_and_netmask()
