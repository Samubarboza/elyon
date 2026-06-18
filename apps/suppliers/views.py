from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event

from apps.suppliers.forms import SupplierForm
from apps.suppliers.models import Supplier
from apps.suppliers.selectors import list_suppliers
from apps.suppliers.services import create_supplier, set_supplier_active, update_supplier
from apps.users.permissions import require_permission


SUPPLIERS_PER_PAGE = 15


@login_required
@require_permission('suppliers.view_supplier')
def supplier_list(request):
    # Entrada desde el menu por HTMX: con permiso navega a la pagina real
    if request.htmx and 'search' not in request.GET and 'page' not in request.GET:
        return HttpResponseClientRedirect(reverse('suppliers:supplier_list'))
    search_text = request.GET.get('search', '')
    suppliers = list_suppliers(search_text)
    suppliers_page = Paginator(suppliers, SUPPLIERS_PER_PAGE).get_page(request.GET.get('page'))
    # La busqueda y el paginado por HTMX solo reemplazan la zona de resultados
    if request.htmx:
        return render(request, 'suppliers/_supplier_results.html', {'suppliers_page': suppliers_page, 'search_text': search_text})
    return render(request, 'suppliers/supplier_list.html', {'suppliers_page': suppliers_page, 'search_text': search_text})


@login_required
@require_permission('suppliers.add_supplier')
def supplier_create(request):
    if request.method == 'GET' and request.htmx:
        return HttpResponseClientRedirect(reverse('suppliers:supplier_create'))
    if request.method == 'POST':
        supplier_form = SupplierForm(request.POST)
        if supplier_form.is_valid():
            create_supplier(supplier_form)
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect_to_supplier_list(request)
        if request.htmx:
            return render(request, 'suppliers/_supplier_form.html', {'form': supplier_form})
    else:
        supplier_form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': supplier_form})


@login_required
@require_permission('suppliers.change_supplier')
def supplier_edit(request, supplier_id):
    supplier_to_edit = get_object_or_404(Supplier, pk=supplier_id)
    if request.method == 'POST':
        supplier_form = SupplierForm(request.POST, instance=supplier_to_edit)
        if supplier_form.is_valid():
            update_supplier(supplier_form)
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect_to_supplier_list(request)
        if request.htmx:
            return render(request, 'suppliers/_supplier_form.html', {'form': supplier_form})
    else:
        supplier_form = SupplierForm(instance=supplier_to_edit)
    return render(request, 'suppliers/supplier_form.html', {'form': supplier_form})


@login_required
@require_permission('suppliers.change_supplier')
def supplier_toggle_active(request, supplier_id):
    if request.method != 'POST':
        return redirect('suppliers:supplier_list')
    supplier_to_change = get_object_or_404(Supplier, pk=supplier_id)
    set_supplier_active(supplier_to_change, not supplier_to_change.is_active)
    if request.htmx:
        return toggle_row_response(request, supplier_to_change, 'Estado del proveedor actualizado.', 'success')
    messages.success(request, 'Estado del proveedor actualizado.')
    return redirect('suppliers:supplier_list')


# Devuelve la fila actualizada y dispara el toast sin recargar
def toggle_row_response(request, supplier_row, toast_message, toast_level):
    response = render(request, 'suppliers/_supplier_row.html', {'supplier_row': supplier_row})
    return trigger_client_event(response, 'show_toast', {'message': toast_message, 'level': toast_level})


# Vuelve al listado respetando si la peticion vino por HTMX
def redirect_to_supplier_list(request):
    if request.htmx:
        return HttpResponseClientRedirect(reverse('suppliers:supplier_list'))
    return redirect('suppliers:supplier_list')
