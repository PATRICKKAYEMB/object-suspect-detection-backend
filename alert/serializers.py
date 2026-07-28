from rest_framework import serializers
from .models import Camera, ObjectType, DetectionEvent

class CameraSerializer(serializers.ModelSerializer):
    """Serializer pour les caméras"""
    class Meta:
        model = Camera
        fields = ['id', 'name', 'camera_code', 'location', 'status', 'created_at']

class ObjectTypeSerializer(serializers.ModelSerializer):
    """Serializer pour les types d'objets"""
    class Meta:
        model = ObjectType
        fields = ['id', 'label', 'slug', 'danger_level', 'created_at']

class DetectionEventSerializer(serializers.ModelSerializer):
    """
    Serializer pour les événements de détection.
    
    """
    
    camera_details = CameraSerializer(source='camera', read_only=True)
    object_details = ObjectTypeSerializer(source='object_type', read_only=True)

    class Meta:
        model = DetectionEvent
        fields = [
            'id', 
            'camera',     
            'object_type',  
            'camera_details', 
            'object_details', 
            'confidence', 
            'image', 
            'timestamp', 
            'processed'
        ]
        read_only_fields = ['id', 'timestamp']