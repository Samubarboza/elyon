from django.db.models import Q

from apps.suppliers.models import Supplier


def list_suppliers(search_text=''):
    suppliers = Supplier.objects.all()
    if search_text:
        suppliers = suppliers.filter(Q(name__icontains=search_text) | Q(document__icontains=search_text))
    return suppliers


# Enganche para purchases: proveedores que se pueden asociar a una compra.
# El saldo y el historial los actualizaran purchases y cash al desarrollarse.
def active_suppliers():
    return Supplier.objects.filter(is_active=True)
