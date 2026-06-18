from django.db.models import Q

from apps.customers.models import Customer


def list_customers(search_text=''):
    customers = Customer.objects.all()
    if search_text:
        customers = customers.filter(Q(name__icontains=search_text) | Q(document__icontains=search_text))
    return customers


# Enganche para sales y quotes: clientes que se pueden asociar a una operacion.
# El saldo y el historial los actualizaran sales, quotes y cash al desarrollarse.
def active_customers():
    return Customer.objects.filter(is_active=True)
