import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass

SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 587
SENDER_EMAIL = "annalikhtar5@mail.ru"
SENDER_PASSWORD = getpass.getpass("Enter your email password: ")

def send_email(receiver_email, subject, message, message_type="plain"):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, message_type))  

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

        print(f"Email ({message_type}) successfully sent to {receiver_email}!")
    except Exception as e:
        print("Error while sending:", e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use: python serverA.py <email>")
        sys.exit(1)

    recipient = sys.argv[1]
    subject = "Test message"

    text_message = "Hi! This is a plain text message."
    html_message = """\
    <html>
        <body>
            <h2 style="color:blue;">Hi!</h2>
            <p>This is an <b>HTML</b> message.</p>
        </body>
    </html>
    """

    send_email(recipient, subject, text_message, "plain")
    send_email(recipient, subject, html_message, "html")
