import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class EmailProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'fetch_emails':
            # Here, initiate the process of fetching emails
            total_emails = 10  # Example total; replace with actual logic
            for i in range(total_emails):
                # Simulate checking an email
                await asyncio.sleep(1)  # Simulating delay
                progress = ((i + 1) / total_emails) * 100
                
                # Simulated email data, replace with actual email fetching logic
                email_data = {
                    'subject': f'Email {i + 1}',
                    'date_sent': '2024-10-28',  # Simulated date
                    'from': 'sender@example.com',  # Simulated sender
                    'description': 'Description here'  # Simulated description
                }

                await self.send(text_data=json.dumps({
                    'progress': progress,
                    'checked_count': i + 1,
                    'new_email': email_data  # Pass the new email data
                }))