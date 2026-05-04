# alert/apps.py
from django.apps import AppConfig

class AlertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alert'

    def ready(self):
        # On utilise le chemin complet à partir de la racine du projet
        
        import alert.signals
        