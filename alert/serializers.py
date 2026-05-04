# alert/serializers.py
from rest_framework import serializers
from .models import Camera, ObjectType, DetectionEvent

class CameraSerializer(serializers.ModelSerializer):
    """Serializer pour les caméras"""
    class Meta:
        model = Camera
        fields = ['id', 'name', 'camera_code', 'location', 'status', 'created_at']

class ObjectTypeSerializer(serializers.ModelSerializer):
    """Serializer pour les types d'objets (IA)"""
    class Meta:
        model = ObjectType
        fields = ['id', 'label', 'slug', 'danger_level', 'created_at']

class DetectionEventSerializer(serializers.ModelSerializer):
    """
    Serializer pour les événements de détection.
    On utilise des PrimaryKeyRelatedField pour permettre au Jetson d'envoyer les IDs,
    mais on affiche les détails complets pour l'application mobile.
    """
    # Pour la lecture (GET) : affiche les objets imbriqués
    camera_details = CameraSerializer(source='camera', read_only=True)
    object_details = ObjectTypeSerializer(source='object_type', read_only=True)

    class Meta:
        model = DetectionEvent
        fields = [
            'id', 
            'camera',          # Utilisé pour l'envoi (ID)
            'object_type',     # Utilisé pour l'envoi (ID)
            'camera_details',  # Utilisé pour l'affichage (Lecture seule)
            'object_details',  # Utilisé pour l'affichage (Lecture seule)
            'confidence', 
            'image', 
            'timestamp', 
            'processed'
        ]
        # Le timestamp est généré automatiquement par le modèle
        read_only_fields = ['id', 'timestamp']