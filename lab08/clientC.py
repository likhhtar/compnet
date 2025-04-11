import socket
from check_sum2 import verify_checksum, add_checksum

SERVER_ADDRESS = ('localhost', 12345)

def client_send_file(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open(filename, 'rb') as f:
        while chunk := f.read(1024):
            packet = add_checksum(chunk)
            sock.sendto(packet, SERVER_ADDRESS)
    
    sock.sendto(b'END', SERVER_ADDRESS)
    print('[Client] Файл отправлен')

def client_receive_file(output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 12346))  # Клиент принимает на своем порте

    with open(output_file, 'wb') as f:
        while True:
            data, _ = sock.recvfrom(2048)
            if data == b'END':
                print('[Client] Получение завершено')
                break

            ok, payload = verify_checksum(data)
            if ok:
                f.write(payload)
                print('[Client] Пакет принят')
            else:
                print('[Client] Пакет поврежден!')

if __name__ == '__main__':
    mode = input('Отправить или получить файл? (send/receive): ').strip()
    if mode == 'send':
        client_send_file('txt_files/1.txt')
    else:
        client_receive_file('txt_files/22.txt')
