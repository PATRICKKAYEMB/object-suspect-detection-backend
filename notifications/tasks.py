from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.models import Notification
from notifications.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(bind=True, max_retries=3)
def send_global_notification_task(self, title, message, detection_event_id=None):
    """
    Envoie une notification à ABSOLUMENT TOUS les utilisateurs enregistrés.
    """
    try:
        # On récupère tout le monde sans filtrage
        users = User.objects.all()
        
        if not users.exists():
            logger.warning("Aucun utilisateur trouvé dans la base de données.")
            return False

        for user in users:
            # 1. Création systématique de la notification en base de données
            notification = Notification.objects.create(
                user=user,
                detection_event_id=detection_event_id,
                title=title,
                message=message,
                channel='all',
                metadata={}
            )

            # 2. Envoi WebSocket (In-App)
            NotificationService._send_in_app_notification(notification)

            # 3. Envoi Push (Firebase)
            NotificationService._send_push_notification(notification, user)

            # 4. Envoi Email
            NotificationService._send_email_notification(notification)

            # 5. Mise à jour du statut final
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()

        logger.info(f"Alerte de sécurité traitée pour {users.count()} utilisateurs.")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la tâche de notification globale : {e}")
        # En cas d'erreur (ex: problème réseau avec Firebase), on réessaie 3 fois
        raise self.retry(exc=e, countdown=10)