from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event

from apps.customers.forms import CustomerForm
from apps.customers.models import Customer
from apps.customers.selectors import list_customers
from apps.customers.services import create_customer, set_customer_active, update_customer
from apps.users.permissions import require_permission


@login_required
@require_permission('customers.view_customer')
def customer_list(request):
    # Entrada desde el menu por HTMX: con permiso navega a la pagina real
    if request.htmx and 'search' not in request.GET:
        return HttpResponseClientRedirect(reverse('customers:customer_list'))
    search_text = request.GET.get('search', '')
    customers = list_customers(search_text)
    # La busqueda por HTMX solo reemplaza las filas de la tabla
    if request.htmx:
        return render(request, 'customers/_customer_table.html', {'customers': customers})
    return render(request, 'customers/customer_list.html', {'customers': customers, 'search_text': search_text})


@login_required
@require_permission('customers.add_customer')
def customer_create(request):
    if request.method == 'GET' and request.htmx:
        return HttpResponseClientRedirect(reverse('customers:customer_create'))
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            create_customer(customer_form)
            messages.success(request, 'Cliente creado correctamente.')
            return redirect_to_customer_list(request)
        if request.htmx:
            return render(request, 'customers/_customer_form.html', {'form': customer_form})
    else:
        customer_form = CustomerForm()
    return render(request, 'customers/customer_form.html', {'form': customer_form})


@login_required
@require_permission('customers.change_customer')
def customer_edit(request, customer_id):
    customer_to_edit = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST, instance=customer_to_edit)
        if customer_form.is_valid():
            update_customer(customer_form)
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect_to_customer_list(request)
        if request.htmx:
            return render(request, 'customers/_customer_form.html', {'form': customer_form})
    else:
        customer_form = CustomerForm(instance=customer_to_edit)
    return render(request, 'customers/customer_form.html', {'form': customer_form})


@login_required
@require_permission('customers.change_customer')
def customer_toggle_active(request, customer_id):
    if request.method != 'POST':
        return redirect('customers:customer_list')
    customer_to_change = get_object_or_404(Customer, pk=customer_id)
    set_customer_active(customer_to_change, not customer_to_change.is_active)
    if request.htmx:
        return toggle_row_response(request, customer_to_change, 'Estado del cliente actualizado.', 'success')
    messages.success(request, 'Estado del cliente actualizado.')
    return redirect('customers:customer_list')


# Devuelve la fila actualizada y dispara el toast sin recargar
def toggle_row_response(request, customer_row, toast_message, toast_level):
    response = render(request, 'customers/_customer_row.html', {'customer_row': customer_row})
    return trigger_client_event(response, 'show_toast', {'message': toast_message, 'level': toast_level})


# Vuelve al listado respetando si la peticion vino por HTMX
def redirect_to_customer_list(request):
    if request.htmx:
        return HttpResponseClientRedirect(reverse('customers:customer_list'))
    return redirect('customers:customer_list')
