import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)



# notifications/consumers.py

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        
        # Si le middleware fonctionne, self.user n'est plus Anonymous
        if self.user and self.user.is_authenticated:
            # 1. On crée un groupe UNIQUE pour cet utilisateur (ex: user_5)
            self.room_group_name = f"user_{self.user.id}"
            
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            
            # 2. Envoyer le vrai compteur au démarrage
            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'unread_count': count
            }))
            print(f" WebSocket: {self.user.username} connecté (Badge: {count})")
        else:
            # Si pas d'auth, on ferme pour protéger AlertGuard
            print(" WebSocket: Échec Auth (Anonyme)")
            await self.close()

    async def send_new_detection(self, event):
        """Appelé par la tâche Celery pour envoyer l'alerte"""
        # On recalcule le badge JUSTE AVANT d'envoyer
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




"""

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1. On essaie de récupérer l'utilisateur
        self.user = self.scope.get("user")
        
        # 2. NOM DU GROUPE
        self.room_group_name = 'security_alerts'
        
        # 3. On accepte la connexion
        await self.accept()
        
        # 4. Rejoindre le groupe global
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        
        print(f" WebSocket Connecté au groupe : {self.room_group_name}")

        # Si l'utilisateur est connecté, on envoie le compteur initial
        if self.user and not self.user.is_anonymous:
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'unread_count': unread_count
            }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            print("❌ WebSocket Déconnecté")

    # Cette méthode est celle appelée par le SIGNAL
    async def send_new_detection(self, event):
        Reçoit l'alerte du signal et l'envoie au mobile avec le compteur
        # On récupère le nombre actuel de non-lus
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
        
        # DEBUG : Est-ce qu'on sait qui est l'utilisateur ?
        print(f"🔍 Calcul du badge pour : {self.user}")

        if not self.user or self.user.is_anonymous:
            print("⚠️ Utilisateur anonyme, renvoi de 0")
            return 0

        # On compte les notifications non lues
        count = Notification.objects.filter(user=self.user, is_read=False).count()
        print(f"📊 Nombre non-lus trouvé en DB : {count}")
        return count
"""
