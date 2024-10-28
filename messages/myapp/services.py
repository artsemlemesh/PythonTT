import imaplib
import email
from .models import EmailMessage

class EmailFetcher:
    def __init__(self, account):
        self.account = account
        self.mail = imaplib.IMAP4_SSL("imap.yandex.ru")  # Configure server as per email provider
    
    def login(self):
        try:
            self.mail.login(self.account.email, self.account.password)
            return True
        except imaplib.IMAP4.error:
            return False
    
    def fetch_messages(self):
        self.mail.select("inbox")
        result, data = self.mail.search(None, "ALL")
        
        for num in data[0].split():
            result, msg_data = self.mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            # Parse and save email content
            self.save_email(msg)
        
    def save_email(self, msg):
        # Extract necessary fields for EmailMessage
        subject = msg["subject"]
        sent_date = msg["date"]
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        # Save email to the database
        EmailMessage.objects.create(
            account=self.account,
            subject=subject,
            sent_date=sent_date,
            received_date=sent_date,
            body=body,
            attachments=[]
        )