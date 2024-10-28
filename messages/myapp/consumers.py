import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import email
import imaplib
class EmailProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'fetch_emails':
            await self.fetch_emails()

    async def fetch_emails(self):
        # Replace these with your actual credentials
        EMAIL = 'bublikteam1@gmail.com'
        PASSWORD = 'nucni2-Bazvos-cenwex'  # Use an App Password if 2FA is enabled

        try:
            # Connect to the Gmail IMAP server
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(EMAIL, PASSWORD)
            mail.select('inbox')

            # Search for all emails
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()

            total_emails = len(email_ids)

            for i, email_id in enumerate(email_ids):
                # Fetch the email by ID
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                # Process the email
                subject = msg['subject']
                date_sent = msg['date']
                from_email = msg['from']
                description = self.get_email_body(msg)

                # Calculate progress
                progress = ((i + 1) / total_emails) * 100

                await self.send(text_data=json.dumps({
                    'progress': progress,
                    'checked_count': i + 1,
                    'new_email': {
                        'subject': subject,
                        'date_sent': date_sent,
                        'from': from_email,
                        'description': description
                    }
                }))
                await asyncio.sleep(1)  # Simulate a delay

            mail.logout()

        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    def get_email_body(self, msg):
        # Get the email body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()
        return ''