import socket
import os
import sys
from datetime import datetime

class FTPClient:
    def __init__(self):
        self.control_socket = None
        self.data_socket = None
        self.pasv_port = None
        self.server_ip = None
        self.logged_in = False
    
    def connect(self, host, port=21):
        """Установка соединения с FTP-сервером"""
        try:
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((host, port))
            self.server_ip = host
            response = self._get_response()
            print(response)
            return response
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return None
    
    def login(self, username='anonymous', password=''):
        """Аутентификация на сервере"""
        self._send_command(f"USER {username}")
        response = self._get_response()
        print(response)
        
        self._send_command(f"PASS {password}")
        response = self._get_response()
        print(response)
        
        if "230" in response:
            self.logged_in = True
        return response
    
    def _send_command(self, command):
        """Отправка команды на сервер"""
        if not self.control_socket:
            raise Exception("Нет подключения к серверу")
        self.control_socket.sendall((command + "\r\n").encode())
    
    def _get_response(self):
        """Получение ответа от сервера"""
        response = ""
        while True:
            part = self.control_socket.recv(1024).decode()
            response += part
            if part.endswith("\r\n"):
                break
        return response.strip()
    
    def _enter_pasv_mode(self):
        """Переход в пассивный режим для передачи данных"""
        self._send_command("PASV")
        response = self._get_response()
        print(response)
        
        if "227" not in response:
            raise Exception("Не удалось перейти в пассивный режим")
        
        # Улучшенный парсинг IP и порта из ответа сервера
        try:
            start = response.find('(')
            end = response.find(')', start)
            if start == -1 or end == -1:
                raise ValueError("Неверный формат ответа PASV")
            
            parts = response[start+1:end].split(',')
            if len(parts) != 6:
                raise ValueError("Неверный формат ответа PASV")
            
            ip = ".".join(parts[:4])
            port = (int(parts[4]) * 256) + int(parts[5])
            
            self.pasv_port = port
            # Закрываем предыдущее соединение, если оно есть
            if self.data_socket:
                self.data_socket.close()
            
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.settimeout(10)  # Устанавливаем таймаут
            self.data_socket.connect((ip, port))  # Используем IP из ответа сервера
        except Exception as e:
            raise Exception(f"Ошибка обработки пассивного режима: {e}")

    def list_files(self):
        """Получение списка файлов и директорий"""
        try:
            self._enter_pasv_mode()
            self._send_command("LIST")
            control_response = self._get_response()
            print(control_response)
            
            if "150" not in control_response:
                raise Exception("Сервер не готов к передаче данных")
            
            # Получение данных
            data = []
            while True:
                try:
                    part = self.data_socket.recv(4096).decode('utf-8', errors='ignore')
                    if not part:
                        break
                    data.append(part)
                except socket.timeout:
                    break
            
            self.data_socket.close()
            response = self._get_response()  # Закрытие передачи
            print(response)
            
            return "".join(data)
        except Exception as e:
            if self.data_socket:
                self.data_socket.close()
            print(f"Ошибка при получении списка файлов: {e}")
            return None
        
    def upload_file(self, local_path, remote_path):
        """Загрузка файла на сервер"""
        if not os.path.exists(local_path):
            print(f"Локальный файл не найден: {local_path}")
            return
        
        try:
            self._enter_pasv_mode()
            self._send_command(f"STOR {remote_path}")
            response = self._get_response()
            print(response)
            
            with open(local_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.data_socket.sendall(data)
            
            self.data_socket.close()
            response = self._get_response()
            print(response)
            return response
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return None
    
    def download_file(self, remote_path, local_path):
        """Скачивание файла с сервера"""
        try:
            self._enter_pasv_mode()
            self._send_command(f"RETR {remote_path}")
            response = self._get_response()
            print(response)
            
            if "550" in response:
                print(f"Файл не найден на сервере: {remote_path}")
                return None
            
            with open(local_path, 'wb') as f:
                while True:
                    data = self.data_socket.recv(4096)
                    if not data:
                        break
                    f.write(data)
            
            self.data_socket.close()
            response = self._get_response()
            print(response)
            return response
        except Exception as e:
            print(f"Ошибка при скачивании файла: {e}")
            return None
    
    def quit(self):
        """Закрытие соединения"""
        if self.control_socket:
            self._send_command("QUIT")
            response = self._get_response()
            print(response)
            self.control_socket.close()
            self.control_socket = None
            self.logged_in = False

def print_help():
    print("\nДоступные команды:")
    print("  connect <host> [port] - подключиться к FTP-серверу")
    print("  login [username] [password] - войти на сервер")
    print("  list - получить список файлов и директорий")
    print("  upload <local_path> <remote_path> - загрузить файл на сервер")
    print("  download <remote_path> <local_path> - скачать файл с сервера")
    print("  quit - отключиться от сервера и выйти")
    print("  help - показать эту справку")
    print("  exit - выйти из программы\n")

def main():
    client = FTPClient()
    print("FTP Client (используйте 'help' для списка команд)")
    
    while True:
        try:
            command = input("ftp> ").strip()
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "connect":
                host = parts[1] if len(parts) > 1 else "test.rebex.net"
                port = int(parts[2]) if len(parts) > 2 else 21
                client.connect(host, port)
            
            elif cmd == "login":
                username = parts[1] if len(parts) > 1 else "demo"
                password = parts[2] if len(parts) > 2 else "password"
                client.login(username, password)
            
            elif cmd == "list":
                if not client.logged_in:
                    print("Сначала выполните вход (команда login)")
                    continue
                files = client.list_files()
                if files:
                    print("\nСодержимое сервера:")
                    print(files)
            
            elif cmd == "upload":
                if not client.logged_in:
                    print("Сначала выполните вход (команда login)")
                    continue
                if len(parts) < 3:
                    print("Использование: upload <local_path> <remote_path>")
                    continue
                client.upload_file(parts[1], parts[2])
            
            elif cmd == "download":
                if not client.logged_in:
                    print("Сначала выполните вход (команда login)")
                    continue
                if len(parts) < 3:
                    print("Использование: download <remote_path> <local_path>")
                    continue
                client.download_file(parts[1], parts[2])
            
            elif cmd == "quit":
                client.quit()
            
            elif cmd == "help":
                print_help()
            
            elif cmd in ["exit", "bye"]:
                client.quit()
                break
            
            else:
                print(f"Неизвестная команда: {cmd}")
                print_help()
        
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()