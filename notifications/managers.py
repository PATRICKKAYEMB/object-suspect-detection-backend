from django.db import models
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class NotificationManager(models.Manager):
    """
    Manager personnalisé pour le modèle Notification.
    """

    def create_notification(self, user, title, message, # Ajout de 'user' ici
                            detection_event=None,
                            channel='all',
                            metadata=None,
                            send_async=True):
        """
        Crée une notification et déclenche son envoi.
        """
        # Import local pour éviter les imports circulaires
        from .models import Notification
        
        metadata = metadata or {}

        # 1. Créer la notification en base (avec l'user !)
        notification = self.create(
            user=user, # INDISPENSABLE
            detection_event=detection_event,
            title=title,
            message=message,
            channel=channel,
            metadata=metadata,
            status='pending'
        )

        if send_async:
            try:
                # 2. Utilisation de la tâche Celery d'envoi
                # Note: Assure-toi d'avoir une tâche qui traite une seule notification
                from .tasks import send_global_notification_task 
                
                # Si c'est pour un utilisateur spécifique, on peut soit créer une nouvelle tâche,
                # soit appeler directement le service si on est déjà dans une tâche.
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