from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.text import slugify

#  User
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'  #  Obligatoire pour se connecter avec l'email
    REQUIRED_FIELDS = ['username'] # Champs demandés lors du createsuperuser

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




# Camera
class Camera(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=100)
    # 🔑 Identifiant unique pour le Jetson (ex: "CAM_ENTREE_01")
    camera_code = models.CharField(max_length=50, unique=True, help_text="ID textuel utilisé par le Jetson")
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.camera_code})"

#  ObjectType
class ObjectType(models.Model):
    label = models.CharField(max_length=100)
    # Identifiant textuel unique (ex: "couteau", "pistolet")
    slug = models.SlugField(max_length=100, unique=True, help_text="Identifiant unique pour l'IA")
    danger_level = models.IntegerField()  # 1 (low) - 5 (critical)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label

#  DetectionEvent
class DetectionEvent(models.Model):
    # On lie toujours aux modèles, mais on utilisera le code/slug pour l'insertion
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="detections")
    object_type = models.ForeignKey(ObjectType, on_delete=models.CASCADE, related_name="detections")

    confidence = models.FloatField()
    image = models.ImageField(upload_to='detections/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.object_type.label} detected by {self.camera.name}"
