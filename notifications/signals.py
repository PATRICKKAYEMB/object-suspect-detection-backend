from django.db.models.signals import post_save

from django.dispatch import receiver
from alert.models import DetectionEvent
from notifications.tasks import send_global_notification_task

@receiver(post_save, sender=DetectionEvent)
def notify_everyone_on_detection(sender, instance, created, **kwargs):
    """
    Déclenche systématiquement une alerte globale dès qu'un objet est enregistré.
    """
    if created:
        # On supprime la vérification 'if instance.object_type.label in suspect_labels'
        
        # 1. Préparation du titre et du message (dynamique selon l'objet)
        title = f" DÉTECTION : {instance.object_type.label}"
        
        confidence_pct = int(instance.confidence * 100)
        
        message = (
            f"Objet détecté : {instance.object_type.label} sur la caméra : {instance.camera.name}. "
            f"Indice de confiance : {confidence_pct}%."
        )

        # 2. Appel du wrapper utils
        # Puisque tu utilises .delay() dans utils.py, assure-toi que Celery tourne.
        send_global_notification_task(
            title=title,
            message=message,
            detection_event_id=instance.id
        )
