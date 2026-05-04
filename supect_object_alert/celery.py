import os
from celery import Celery

# 1. Définit le module de réglages par défaut pour le programme 'celery'
# Assure-toi que le nom 'supect_object_alert.settings' correspond bien au dossier de ton projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supect_object_alert.settings')

app = Celery('supect_object_alert')

# 2. Utilise une chaîne de caractères ici pour que le worker n'ait pas à sérialiser
# l'objet de configuration. Le namespace='CELERY' signifie que toutes les clés de 
# configuration de Celery dans settings.py doivent commencer par 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 3. Charge automatiquement les tâches (tasks.py) de toutes les applications Django enregistrées.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """
    Tâche de test pour vérifier que Celery communique bien avec Django.
    Tu pourras la lancer avec debug_task.delay() dans ton shell.
    """
    print(f'Request: {self.request!r}')