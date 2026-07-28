# notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .managers import NotificationManager
from alert.models import DetectionEvent

User = get_user_model()

class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    
    detection_event = models.ForeignKey(
        DetectionEvent,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True, 
        blank=True
    )
    
    CHANNEL_CHOICES = [
        ('in_app', 'In-App'),
        ('push', 'Push Notification'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('all', 'Tous les canaux')
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('failed', 'Échec'),
        ('skipped', 'Ignoré'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='all')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True) 
    sent_at = models.DateTimeField(null=True, blank=True)
    
    objects = NotificationManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']), # Index composé pour la rapidité
            models.Index(fields=['created_at']),
            models.Index(fields=['channel']), 
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.title}"

    def mark_as_read(self):
        """Marque la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class DeviceFcmToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_tokens')
    fcm_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
  
    class Meta:
        unique_together = ('user', 'fcm_token')