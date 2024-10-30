import imaplib
import email
from .models import EmailMessage, EmailAccount
from email.header import decode_header
from dateutil import parser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
import os
import re
from bs4 import BeautifulSoup  

class EmailFetcher:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")  # Configure server as per email provider
    

    def login(self):
        print("Logging in...")
        try:
            self.mail.login(self.email, self.password)  # Use provided email and password
            print("Login successful!")
            return True
        except imaplib.IMAP4.error as e:
            print(f"Login failed! Error: {e}")  # Corrected string formatting
            return False

    # def login(self):
    #     print("Logging in...")
    #     try:
    #         self.mail.login('bublikteam1@gmail.com', 'bzdy wyke ygzy uygm')
    #         print("Login successful!")
    #         return True
    #     except imaplib.IMAP4.error as e:
    #         print("Login failed! Error: {e}")
    #         return False
    
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
        
           
          
        # Process email content and handle multipart
            content = ""
            attachments = []
            attachments_dir = os.path.join(settings.MEDIA_ROOT, 'attachments')

            # Ensure the 'attachments' directory exists
            if not os.path.exists(attachments_dir):
                os.makedirs(attachments_dir)

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Save attachment if it’s not inline
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            # Decode filename if encoded
                            filename = self.decode_subject(filename)
                            file_data = part.get_payload(decode=True)

                            # Save to Django storage (e.g., to media folder)
                            file_path = os.path.join(attachments_dir, filename)
                            with open(file_path, 'wb') as f:
                                f.write(file_data)
                            attachments.append(file_path)
                    elif content_type == "text/plain":
                        # Get the text content
                        payload = part.get_payload(decode=True)
                        if payload:
                            content += payload.decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        # Handle HTML content, strip HTML tags if needed
                        payload = part.get_payload(decode=True)
                        if payload:
                            # Parse HTML and extract text
                            soup = BeautifulSoup(payload, 'html.parser')
                            for a in soup.find_all('a'):
                                a.decompose()  # Remove the link
                            for img in soup.find_all('img'):
                                img.decompose()  # Remove the image
                            content += soup.get_text(strip=True)  # Get plain text from HTML

            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    content = payload.decode('utf-8', errors='ignore')
            
            # Save the email details
            saved_count += self.save_email(msg, parsed_date, content, index + 1, total_messages, attachments)
        print(f"Successfully saved {saved_count} messages.")  # Log the number of saved messages
    
    
    def save_email(self, msg, parsed_date, content, current_index, total_messages, attachments=[]):
        raw_subject = msg.get("Subject", "No Subject")
        subject = self.decode_subject(raw_subject)
        from_ = msg.get("From", "Unknown Sender")
        
        # Extract email address from the 'From' field
        email_address = self.extract_email_address(from_)

        account, created = EmailAccount.objects.get_or_create(email=email_address)
        limited_content = self.limit_content(content, 5)

        # Create and save the EmailMessage instance
        email_message = EmailMessage(
            account=account,
            subject=subject,
            sent_date=parsed_date,
            received_date=parsed_date,
            body=limited_content,
            attachments=attachments
        )
        email_message.save()

        # Notify progress via WebSocket
        self.notify_progress(current_index, total_messages, email_message)
        # time.sleep(1)
        return 1  # Indicate that one email was saved

    def notify_progress(self, current_index, total_messages, email_message):
        progress_percentage = (current_index / total_messages) * 100
        message = {
            "subject": email_message.subject,
            "date_sent": email_message.sent_date.isoformat() if email_message.sent_date else "Unknown",
            "from": email_message.account.email,
            "description": email_message.body,
            "received_date": email_message.received_date.isoformat() if email_message.received_date else "Unknown",
            "attachments": email_message.attachments
        }

    # Send to WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('email_updates', {
            'type': 'send_progress',
            'progress': progress_percentage,
            'checked_count': current_index,
            'new_email': message
        })

    def extract_email_address(self, from_str):
        """Extracts the email address from the 'From' field."""
        match = re.search(r'<(.+?)>', from_str)
        if match:
            return match.group(1)  # Return the email address inside the angle brackets
        return from_str  # Return the original string if no email address is found

    def clean_content(content):
        cleaned = re.sub(r'[^a-zA-Z0-9\s,.!?;:\'\"]', '', content)  # Adjust as necessary
        return cleaned.strip()  # Remove leading and trailing whitespace

    def decode_subject(self, raw_subject):
        """Decode the MIME-encoded email subject line into a readable format."""
        decoded_parts = decode_header(raw_subject)
        subject = ''
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                # Decode using the specified encoding or default to 'utf-8'
                subject += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                subject += part
        
        return subject


    
    def limit_content(self, content, word_limit):
        words = content.split()
        limited_content = ' '.join(words[:word_limit])
        return limited_content