import socket
from check_sum2 import verify_checksum, add_checksum

def server_receive_file(output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 12345))

    with open(output_file, 'wb') as f:
        while True:
            data, addr = sock.recvfrom(2048)
            if data == b'END':
                print('[Server] Получение завершено')
                break

            ok, payload = verify_checksum(data)
            if ok:
                f.write(payload)
                print('[Server] Пакет принят')
            else:
                print('[Server] Пакет поврежден!')

def server_send_file(filename, client_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(filename, 'rb') as f:
        while chunk := f.read(1024):
            packet = add_checksum(chunk)
            sock.sendto(packet, client_address)

    sock.sendto(b'END', client_address)
    print('[Server] Файл отправлен')

if __name__ == '__main__':
    mode = input('Отправить или получить файл? (send/receive): ').strip()
    if mode == 'receive':
        server_receive_file('txt_files/11.txt')
    else:
        client_ip = input('Введите IP клиента: ')
        client_port = int(input('Введите порт клиента: '))
        server_send_file('txt_files/2.txt', (client_ip, client_port))
