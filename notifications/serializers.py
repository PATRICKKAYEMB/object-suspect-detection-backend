from rest_framework import serializers
from .models import Notification, DeviceFcmToken
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications - Adapté à ton modèle réel"""
    time_ago = serializers.SerializerMethodField()
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    
    class Meta:
        model = Notification
        
        fields = [
            'id', 'title', 'message', 'channel', 'channel_display', 
            'status', 'is_read', 'metadata', 'created_at', 'read_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

    def get_time_ago(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        if obj.created_at:
            return timesince(obj.created_at, timezone.now())
        return None

class MarkAsReadSerializer(serializers.Serializer):
    """Serializer pour marquer les notifications comme lues"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=True
    )
    read = serializers.BooleanField(default=True)

class BulkNotificationSerializer(serializers.Serializer):
    """Serializer pour l'envoi de notifications en masse par admin"""
    user_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    title = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    channel = serializers.ChoiceField(
        choices=Notification.CHANNEL_CHOICES,
        default='in_app'
    )
    data = serializers.DictField(required=False, default=dict)

class DeviceFcmTokenSerializer(serializers.ModelSerializer):
    """Serializer pour les tokens FCM"""
    class Meta:
        model = DeviceFcmToken
        fields = ['id', 'user', 'fcm_token', 'created_at']
        read_only_fields = ['id', 'created_at']