import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "security_alerts"
        # On ajoute l'utilisateur au groupe des alertes
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Cette méthode reçoit l'alerte du Signal et l'envoie au mobile
    async def send_new_detection(self, event):
        await self.send(text_data=json.dumps(event["content"]))