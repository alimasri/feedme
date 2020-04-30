import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from emailclients.emailclient import EmailClient


class SMTPClient(EmailClient):

    def __init__(self, host, port, login, password):
        self.login = login
        self.password = password
        self.host = host
        self.port = port

    def create_message(self, sender, to, subject, message_text):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = to
        content = MIMEText(message_text, "html")
        message.attach(content)
        return message

    def send_message(self, message):
        with smtplib.SMTP(self.host, self.port) as server:
            server.login(self.login, self.password)
            server.sendmail(message["From"], message["To"], message.as_string())
