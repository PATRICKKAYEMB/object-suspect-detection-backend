import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supect_object_alert.settings')

app = Celery('supect_object_alert')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """
    Tâche de test pour vérifier que Celery communique bien avec Django.
    Tu pourras la lancer avec debug_task.delay() dans ton shell.
    """
    print(f'Request: {self.request!r}')