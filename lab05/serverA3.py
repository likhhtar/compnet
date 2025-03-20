import socket
import ssl
import base64
import getpass
import os

SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 465
SENDER_EMAIL = "annalikhtar5@mail.ru"
SENDER_PASSWORD = "a348ifj1arRNWfxZr0rK"
RECEIVER_EMAIL = "likhhtar@gmail.com"
IMAGE_PATH = "img/image.jpg"

with open(IMAGE_PATH, "rb") as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode()

boundary = "----=_NextPart_001_"

message = f"""From: {SENDER_EMAIL}
To: {RECEIVER_EMAIL}
Subject: Тестовое письмо с изображением
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="{boundary}"

--{boundary}
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 7bit

Привет! Это письмо содержит изображение во вложении.

--{boundary}
Content-Type: image/jpeg; name="{os.path.basename(IMAGE_PATH)}"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="{os.path.basename(IMAGE_PATH)}"

{encoded_image}

--{boundary}--
"""

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

        server.sendall(message.encode() + b"\r\n.\r\n")
        print(server.recv(1024).decode())
        server.sendall(b"QUIT\r\n")
        print(server.recv(1024).decode())
