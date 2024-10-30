import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EmailProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("email_updates", self.channel_name)
        await self.accept()
        print(f"WebSocket connection established: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("email_updates", self.channel_name)

    async def send_progress(self, event):
        progress = event['progress']
        checked_count = event['checked_count']
        await self.send(text_data=json.dumps({
            'progress': progress,
            'checked_count': checked_count,
            'new_email': event.get('new_email', None)
        }))

