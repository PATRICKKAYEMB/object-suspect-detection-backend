# supect_object_alert/asgi.py
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Importe ton nouveau middleware
from notifications.middleware import JWTAuthMiddleware 
from notifications.routing import notifications_ws

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supect_object_alert.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    
    "websocket": JWTAuthMiddleware(
        URLRouter(
            notifications_ws
        )
    ),
})
