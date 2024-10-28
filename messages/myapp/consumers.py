import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EmailProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("email_progress", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("email_progress", self.channel_name)

    async def update_progress(self, event):
        await self.send(text_data=json.dumps({
            "progress": event["progress"]
        }))