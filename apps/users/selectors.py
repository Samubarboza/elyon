from apps.users.models import User


# El superuser dueno del sistema nunca es visible ni gestionable desde el programa
def company_users():
    return User.objects.filter(is_superuser=False)


def count_active_users():
    return company_users().filter(is_active=True).count()


def list_users():
    return company_users().order_by('username')
