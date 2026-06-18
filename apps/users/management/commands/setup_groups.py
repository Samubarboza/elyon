from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


# Grupos iniciales del sistema, uno por modulo de acceso
GROUPS = [
    'Administración',
    'Ventas',
    'Caja',
    'Inventario',
    'Reportes',
    'Clientes',
    'Usuarios',
    'Configuración',
]

# Permisos por grupo segun los modelos que ya existen.
# Cada modulo nuevo agregara aca sus permisos cuando se desarrolle.
GROUP_PERMISSIONS = {
    'Administración': ['add_user', 'change_user', 'view_user', 'view_group'],
    'Usuarios': ['add_user', 'change_user', 'view_user', 'view_group'],
    'Configuración': ['view_company', 'change_company'],
    'Clientes': ['add_customer', 'change_customer', 'view_customer'],
}


class Command(BaseCommand):
    help = 'Crea los grupos iniciales y asigna sus permisos'

    def handle(self, *args, **options):
        for group_name in GROUPS:
            group, was_created = Group.objects.get_or_create(name=group_name)
            permission_codenames = GROUP_PERMISSIONS.get(group_name, [])
            self.assign_permissions(group, permission_codenames)
            if was_created:
                self.stdout.write('Grupo creado: ' + group_name)
            else:
                self.stdout.write('Grupo actualizado: ' + group_name)

    def assign_permissions(self, group, permission_codenames):
        found_permissions = Permission.objects.filter(codename__in=permission_codenames)
        group.permissions.set(found_permissions)
        found_codenames = set(found_permissions.values_list('codename', flat=True))
        for missing_codename in set(permission_codenames) - found_codenames:
            self.stdout.write(self.style.WARNING('Permiso no encontrado: ' + missing_codename))
