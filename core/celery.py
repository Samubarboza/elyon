# creamos, configuramos, conectamos nuestra app de celery con el proyecto django
# dejamos listo para poder ejecutar tareas en segundo plano

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core', include=['core.tasks'])
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
