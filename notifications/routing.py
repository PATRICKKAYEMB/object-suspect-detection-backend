from django.urls import re_path
from notifications import consumers as notification_consumers


notifications_ws = [
    
    re_path(r'ws/notifications/$', notification_consumers.NotificationConsumer.as_asgi()), 
   
]