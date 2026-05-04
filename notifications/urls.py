from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceFcmTokenViewSet, NotificationViewSet

router = DefaultRouter()
# Route pour lister et supprimer les notifications
router.register(r'', NotificationViewSet, basename='notification')
# Route pour enregistrer les tokens Firebase (FCM)
router.register(r'fcm-tokens', DeviceFcmTokenViewSet, basename='fcm-tokens')

urlpatterns = [
    path('', include(router.urls)),

    # Actions spécifiques pour la gestion des notifications
    path('mark-as-read/', NotificationViewSet.as_view({'post': 'mark_as_read'}), name='notifications-mark-as-read'),
    path('mark-all-as-read/', NotificationViewSet.as_view({'post': 'mark_all_as_read'}), name='notifications-mark-all-as-read'),
    path('clear-all/', NotificationViewSet.as_view({'delete': 'clear_all'}), name='notifications-clear-all'),
]



