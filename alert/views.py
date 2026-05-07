from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth import authenticate

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import DetectionEvent
from .serializers import DetectionEventSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# ==========================
# AUTHENTIFICATION
# ==========================

class ConnexionAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        #print(f"--- DATA REÇUE ---")
        #print(f"Type: {type(request.data)}")
        #print(f"Contenu: {request.data}")
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "L'email et le mot de passe sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"error": "Identifiants invalides."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Connexion réussie",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)

# ==========================
# DETECTION EVENTS VIEWSET
# ==========================

class DetectionEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DetectionEventSerializer

    def get_queryset(self):
        return DetectionEvent.objects.select_related(
            "camera",
            "object_type"
        ).all().order_by("-timestamp")

    # --------------------------
    # CREATE 
    # --------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # LIST (Avec filtres)
    # --------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        category = request.query_params.get("category")
        date_start = request.query_params.get("date_start")
        date_end = request.query_params.get("date_end")

        if category:
            queryset = queryset.filter(object_type__label__icontains=category)

        if date_start and date_end:
            try:
                queryset = queryset.filter(
                    timestamp__date__range=[date_start, date_end]
                )
            except Exception:
                return Response(
                    {"error": "Format de date invalide. Utilisez YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # --------------------------
    # STATS 
    # --------------------------
    @action(detail=False, methods=["get"])
    def stats(self, request):
        queryset = DetectionEvent.objects.all()

        today = timezone.now().date()
        last_7_days = timezone.now() - timedelta(days=7)

        total_events = queryset.count()

        today_events = queryset.filter(timestamp__date=today).count()

        last_7_days_events = queryset.filter(timestamp__gte=last_7_days).count()

        events_by_camera = queryset.values(
            "camera__name"
        ).annotate(total=Count("id")).order_by('-total')

        events_by_object_today = queryset.filter(
            timestamp__date=today
        ).values(
            "object_type__label"
        ).annotate(total=Count("id")).order_by('-total')

        return Response({
            "total_events": total_events,
            "today_events": today_events,
            "last_7_days_events": last_7_days_events,
            "events_by_camera": list(events_by_camera),
            "events_by_object_today": list(events_by_object_today)
        })
