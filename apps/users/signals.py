import logging

from axes.signals import user_locked_out
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger('apps.users')


def get_client_ip(request):
    if request is None:
        return 'desconocida'
    return request.META.get('REMOTE_ADDR', 'desconocida')


@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    logger.info('Inicio de sesion correcto: usuario %s desde %s', user.get_username(), get_client_ip(request))


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    username = user.get_username() if user else 'desconocido'
    logger.info('Cierre de sesion: usuario %s', username)


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'desconocido')
    logger.warning('Intento de inicio de sesion fallido: usuario %s desde %s', username, get_client_ip(request))


@receiver(user_locked_out)
def log_lockout(sender, **kwargs):
    username = kwargs.get('username', 'desconocido')
    ip_address = kwargs.get('ip_address', 'desconocida')
    logger.warning('Acceso bloqueado por intentos fallidos: usuario %s desde %s', username, ip_address)
