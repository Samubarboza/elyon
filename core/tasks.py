from celery import shared_task

# tarea d eprueba
@shared_task
def check_celery_connection():
    return 'Celery funcionando correctamente'
