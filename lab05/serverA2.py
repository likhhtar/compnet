import socket
import ssl
import base64
import getpass

SMTP_SERVER = "smtp.mail.ru"  
SMTP_PORT = 465
SENDER_EMAIL = "annalikhtar5@mail.ru"
SENDER_PASSWORD = getpass.getpass("Enter your email password: ")
RECEIVER_EMAIL = "likhhtar@gmail.com"

context = ssl.create_default_context()
with socket.create_connection((SMTP_SERVER, SMTP_PORT)) as sock:
    with context.wrap_socket(sock, server_hostname=SMTP_SERVER) as server:

        print(server.recv(1024).decode())

        server.sendall(b"EHLO example.com\r\n")
        print(server.recv(1024).decode())

        server.sendall(b"AUTH LOGIN\r\n")
        print(server.recv(1024).decode())

        server.sendall(base64.b64encode(SENDER_EMAIL.encode()) + b"\r\n")
        print(server.recv(1024).decode())

        server.sendall(base64.b64encode(SENDER_PASSWORD.encode()) + b"\r\n")
        print(server.recv(1024).decode())

        server.sendall(f"MAIL FROM:<{SENDER_EMAIL}>\r\n".encode())
        print(server.recv(1024).decode())

        server.sendall(f"RCPT TO:<{RECEIVER_EMAIL}>\r\n".encode())
        print(server.recv(1024).decode())

        server.sendall(b"DATA\r\n")
        print(server.recv(1024).decode())

        message = f"""\
From: {SENDER_EMAIL}
To: {RECEIVER_EMAIL}
Subject: Тестовое письмо от сокет-клиента

Привет! Это письмо отправлено через SMTP-сервер с использованием чистых сокетов.
"""
        server.sendall(message.encode() + b"\r\n.\r\n")  
        print(server.recv(1024).decode())

        server.sendall(b"QUIT\r\n")
        print(server.recv(1024).decode())
