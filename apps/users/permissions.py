import logging
from functools import wraps

from django.core.exceptions import PermissionDenied

from apps.users.signals import get_client_ip

logger = logging.getLogger('apps.users')


# Valida el permiso del usuario y registra los accesos no autorizados
def require_permission(permission_codename):
    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(permission_codename):
                logger.warning('Acceso no autorizado: usuario %s desde %s intento %s', request.user.get_username(), get_client_ip(request), permission_codename)
                raise PermissionDenied
            return view_function(request, *args, **kwargs)
        return wrapped_view
    return decorator
