from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Notification, DeviceFcmToken
from .serializers import (
    NotificationSerializer, 
  
    DeviceFcmTokenSerializer,
    MarkAsReadSerializer
)
from .tasks import send_global_notification_task

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Gestion des notifications de l'utilisateur.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def mark_as_read(self, request):
        """Marquer des notifications spécifiques comme lues avec validation"""
        serializer = MarkAsReadSerializer(data=request.data)
        if serializer.is_valid():
            notification_ids = serializer.validated_data['notification_ids']
            read_status = serializer.validated_data['read']

            updated_count = self.get_queryset().filter(id__in=notification_ids).update(
                is_read=read_status,
                read_at=timezone.now() if read_status else None
            )
            return Response({
                'message': f'{updated_count} notification(s) mise(s) à jour.',
                'updated_count': updated_count
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        updated_count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'updated_count': updated_count})

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        deleted_count, _ = self.get_queryset().delete()
        return Response({'deleted_count': deleted_count}, status=status.HTTP_204_NO_CONTENT)



class DeviceFcmTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Enregistre ou met à jour un token FCM.
    """
    queryset = DeviceFcmToken.objects.all()
    serializer_class = DeviceFcmTokenSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        token = self.request.data.get('fcm_token')
        DeviceFcmToken.objects.filter(user=self.request.user, fcm_token=token).delete()
        serializer.save(user=self.request.user)