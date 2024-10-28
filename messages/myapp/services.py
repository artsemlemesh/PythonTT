import imaplib
import email
from .models import EmailMessage

class EmailFetcher:
    def __init__(self, account):
        self.account = account
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")  # Configure server as per email provider
    
    def login(self):
        print("Logging in...")
        try:
            self.mail.login('bublikteam1@gmail.com', 'bzdy wyke ygzy uygm')
            print("Login successful!")
            return True
        except imaplib.IMAP4.error as e:
            print("Login failed! Error: {e}")
            return False
    
    def fetch_messages(self):
        print("Fetching messages...")
        self.mail.select("inbox")
        result, data = self.mail.search(None, "ALL")
        
        for num in data[0].split():
            result, msg_data = self.mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            # Parse and save email content
            self.save_email(msg)
        
    def save_email(self, msg):
        # print('save email',  msg)
        # Extract necessary fields for EmailMessage
        subject = msg["subject"]
        sent_date = msg["date"]
    # Ensure there's a payload to decode
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='ignore')
        else:
            body = ""        
        # Save email to the database
        EmailMessage.objects.create(
            account=self.account,
            subject=subject,
            sent_date=sent_date,
            received_date=sent_date,
            body=body,
            attachments=[]
        )