# notifications/middleware.py
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model # <--- CHANGE CECI
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

# Récupère ton modèle utilisateur personnalisé (alert.User)
User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token:
            try:
                # Utilise la SECRET_KEY de ton settings.py
                decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                
                # Vérifie si ton JWT utilise 'user_id' ou 'id'
                user_id = decoded_data.get("user_id") or decoded_data.get("id")
                
                if user_id:
                    scope["user"] = await get_user(user_id)
                else:
                    scope["user"] = AnonymousUser()
                    
            except Exception as e:
                print(f" Erreur JWT Middleware: {e}")
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
