from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import DetectionEvent
from .serializers import DetectionEventSerializer

@receiver(post_save, sender=DetectionEvent)
def broadcast_detection(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
      
        serializer = DetectionEventSerializer(instance)
        
        async_to_sync(channel_layer.group_send)(
            "security_alerts",
            {
                "type": "send_new_detection",
                "content": {
                    "type": "NEW_DETECTION",
                    "data": serializer.data
                }
            }
        )