from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.text import slugify


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    groups = models.ManyToManyField(
        Group,
        related_name='alert_users',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='alert_user_permissions',
        blank=True,
    )

    def __str__(self):
        return self.username





class Camera(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    latitude= models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)

    def __str__(self):
        return f"{self.name}"


class ObjectType(models.Model):
    label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label

#  DetectionEvent
class DetectionEvent(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="detections")
    object_type = models.ForeignKey(ObjectType, on_delete=models.CASCADE, related_name="detections")

    confidence = models.FloatField()
    image = models.ImageField(upload_to='detections/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.object_type.label} detected by {self.camera.name}"
