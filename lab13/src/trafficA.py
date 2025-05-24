import psutil
import time

def get_bytes():
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv

def format_bytes(n):
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if n < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} ТБ"

def main():
    print("Подсчёт сетевого трафика\n")
    sent_old, recv_old = get_bytes()

    try:
        while True:
            time.sleep(1)
            sent_new, recv_new = get_bytes()

            sent_diff = sent_new - sent_old
            recv_diff = recv_new - recv_old

            print(f"Исходящий: {format_bytes(sent_diff):>12} | Входящий: {format_bytes(recv_diff):>12}")

            sent_old, recv_old = sent_new, recv_new
    except KeyboardInterrupt:
        print("\n⏹ Завершено пользователем.")

if __name__ == "__main__":
    main()
