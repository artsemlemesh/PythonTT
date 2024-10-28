import imaplib
import email
from email.header import decode_header
from django.conf import settings

class EmailClient:
    def __init__(self, email_service, username, password):
        service = settings.EMAIL_SERVICES[email_service]
        self.imap_server = service['IMAP_SERVER']
        self.imap_port = service['IMAP_PORT']
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            print("Connection failed:", e)
            return False

    def fetch_emails(self, last_email_uid=None):
        emails = []
        try:
            self.connection.select("inbox")
            # Search for all emails
            result, data = self.connection.search(None, "ALL")

            if result == "OK":
                for num in data[0].split():
                    res, msg_data = self.connection.fetch(num, "(RFC822)")
                    if res != "OK":
                        continue

                    msg = email.message_from_bytes(msg_data[0][1])
                    email_data = {
                        "subject": decode_header(msg["Subject"])[0][0],
                        "date": msg["Date"],
                        "from": msg["From"],
                        "body": self.get_email_body(msg),
                    }
                    emails.append(email_data)

            return emails
        except Exception as e:
            print("Error fetching emails:", e)
            return []

    def get_email_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" and "attachment" not in part.get("Content-Disposition", ""):
                    return part.get_payload(decode=True).decode("utf-8", errors="ignore")
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")

    def logout(self):
        if self.connection:
            self.connection.logout()