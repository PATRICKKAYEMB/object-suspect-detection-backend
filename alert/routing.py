from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import DetectionEventViewSet, ConnexionAPIView


router = DefaultRouter()
router.register(r'detection-events', DetectionEventViewSet, basename='detection-events')


urlpatterns = [
    path("", include(router.urls)),
    path("connexion/", ConnexionAPIView.as_view(), name="connexion"),
]