import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)





class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        
        if self.user and self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
            
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            
            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'unread_count': count
            }))
            print(f" WebSocket: {self.user.username} connecté (Badge: {count})")
        else:
            print(" WebSocket: Échec Auth (Anonyme)")
            await self.close()

    async def send_new_detection(self, event):
        """Appelé par la tâche Celery pour envoyer l'alerte"""
      
        unread_count = await self.get_unread_count()
        
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['content'],
            'unread_count': unread_count,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()


