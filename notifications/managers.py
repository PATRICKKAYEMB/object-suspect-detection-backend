from django.db import models
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class NotificationManager(models.Manager):
    """
    Manager personnalisé pour le modèle Notification.
    """

    def create_notification(self, user, title, message, 
                            detection_event=None,
                            channel='all',
                            metadata=None,
                            send_async=True):
        """
        Crée une notification et déclenche son envoi.
        """
        
        from .models import Notification
        
        metadata = metadata or {}

        notification = self.create(
            user=user, 
            detection_event=detection_event,
            title=title,
            message=message,
            channel=channel,
            metadata=metadata,
            status='pending'
        )

        if send_async:
            try:
                from .tasks import send_global_notification_task 
                logger.info(f"Notification {notification.id} créée pour {user.username}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la notification {notification.id}: {e}")

        return notification

    def mark_all_as_read(self, user):
        """Méthode utilitaire pour le manager"""
        return self.filter(user=user, is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )