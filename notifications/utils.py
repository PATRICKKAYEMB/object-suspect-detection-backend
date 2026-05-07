# notifications/utils.py

from notifications.tasks import send_global_notification_task
import logging

logger = logging.getLogger(__name__)


def notify_security_team(title, message, detection_event_id=None):
    """
    Lance la tâche Celery pour alerter uniquement l'équipe de sécurité.
    """
    try:
        task = send_global_notification_task.delay(
            title=title,
            message=message,
            detection_event_id=detection_event_id
        )
        logger.info(f"Alerte de sécurité envoyée à la file d'attente (Task ID: {task.id})")
        return task.id
    except Exception as e:
        logger.error(f"Echec critique lors du lancement de l'alerte : {e}")
        return None