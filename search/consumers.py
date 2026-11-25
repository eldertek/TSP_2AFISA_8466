import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.connection_id = f"user_{user.id}"
            await self.channel_layer.group_add(self.connection_id, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "connection_id"):
            await self.channel_layer.group_discard(
                self.connection_id, self.channel_name
            )

    async def notify(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
