from django.db.models import Q

from apps.customers.models import Customer


def list_customers(search_text=''):
    customers = Customer.objects.all()
    if search_text:
        customers = customers.filter(Q(name__icontains=search_text) | Q(document__icontains=search_text))
    return customers


def active_customers():
    return Customer.objects.filter(is_active=True)
