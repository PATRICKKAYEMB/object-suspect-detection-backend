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

        title = f" DÉTECTION : {instance.object_type.label}"
        
        confidence_pct = int(instance.confidence * 100)
        
        message = (
            f"Objet détecté : {instance.object_type.label} sur la caméra : {instance.camera.name}. "
            f"Indice de confiance : {confidence_pct}%."
        )

        send_global_notification_task(
            title=title,
            message=message,
            detection_event_id=instance.id
        )
