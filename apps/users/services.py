import logging

from apps.users.models import Company
from apps.users.selectors import count_active_users

logger = logging.getLogger('apps.users')


class UserActionError(Exception):
    pass


def plan_limit_reached():
    company = Company.get_config()
    return count_active_users() >= company.max_users


def limit_message():
    company = Company.get_config()
    return 'Se alcanzó el límite de usuarios del plan ' + company.plan.name + '. No se pueden crear más usuarios.'


# Los usuarios del sistema nunca entran al panel de administracion de Django
def create_user(user_form):
    if plan_limit_reached():
        raise UserActionError(limit_message())
    new_user = user_form.save(commit=False)
    new_user.is_staff = False
    new_user.is_superuser = False
    new_user.save()
    user_form.save_m2m()
    logger.info('Usuario creado: %s', new_user.get_username())
    return new_user


def update_user(user_form):
    updated_user = user_form.save()
    logger.info('Usuario actualizado: %s', updated_user.get_username())
    return updated_user


def set_user_active(user_to_change, is_active):
    if not is_active and user_to_change.is_main_admin:
        raise UserActionError('No se puede desactivar al administrador principal.')
    if is_active and plan_limit_reached():
        raise UserActionError(limit_message())
    user_to_change.is_active = is_active
    user_to_change.save(update_fields=['is_active'])
    logger.info('Estado de usuario actualizado: %s activo=%s', user_to_change.get_username(), is_active)
    return user_to_change
