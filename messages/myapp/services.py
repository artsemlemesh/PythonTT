import imaplib
import email
from .models import EmailMessage, EmailAccount
from datetime import datetime
from email.header import decode_header
from dateutil import parser
import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


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

        message_nums = data[0].split()
        last_10_nums = message_nums[-10:]  # Get last 10 message numbers

        total_messages = len(last_10_nums)
        saved_count = 0  # Counter for successfully saved messages

        for index, num in enumerate(last_10_nums):
            result, msg_data = self.mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
        
        # Parse the date
            raw_date = msg.get("Date")
            parsed_date = parser.parse(raw_date) if raw_date else None
        
            # if raw_date:
            #     try:
            #         parsed_date = parser.parse(raw_date)
            #     except Exception as e:
            #         print(f"Could not parse date: {raw_date} - Error: {e}")
            #         parsed_date = None

        # Process email content and handle multipart
            content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            content += payload.decode('utf-8', errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    content = payload.decode('utf-8', errors='ignore')
            
            # Save the email details
            saved_count += self.save_email(msg, parsed_date, content, index + 1, total_messages)
            # time.sleep(1)
        print(f"Successfully saved {saved_count} messages.")  # Log the number of saved messages
    
    
    def save_email(self, msg, parsed_date, content, current_index, total_messages):
        subject = msg.get("Subject", "No Subject")
        from_ = msg.get("From", "Unknown Sender")
        
        account, created = EmailAccount.objects.get_or_create(email=from_)
        limited_content = self.limit_content(content, 5)

        # Create and save the EmailMessage instance
        email_message = EmailMessage(
            account=account,
            subject=subject,
            sent_date=parsed_date,
            received_date=parsed_date,
            body=limited_content,
            attachments=[]
        )
        email_message.save()

        # Notify progress via WebSocket
        self.notify_progress(current_index, total_messages, email_message)
        # time.sleep(1)
        return 1  # Indicate that one email was saved

    def notify_progress(self, current_index, total_messages, email_message):
        progress_percentage = (current_index / total_messages) * 100
        print(f"Progress: {progress_percentage:.2f}%")
        message = {
            "progress": progress_percentage,
            "new_email": {
                "subject": email_message.subject,
                "date_sent": email_message.sent_date.isoformat() if email_message.sent_date else "Unknown",
                "from": email_message.account.email,
                "description": email_message.body,
                "received_date": email_message.received_date.isoformat() if email_message.received_date else "Unknown",  # Added if needed
                "attachments": email_message.attachments  # If you want to include attachments
            }
        }

    # Send to WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('email_updates', {
            'type': 'send_progress',
            'progress': progress_percentage,
            'new_email': message['new_email']
        })

    
    def decode_header(self, header):
        """
        Decode an email header into a string.
        """
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):  # Only decode bytes
                # Decode the bytes using the specified encoding, default to 'utf-8'
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += part  # If it's already a string, just add it
        
        return decoded_string
    
    def limit_content(self, content, word_limit):
        words = content.split()
        limited_content = ' '.join(words[:word_limit])
        return limited_content