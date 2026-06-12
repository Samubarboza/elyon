from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event

from apps.users.forms import UserCreateForm, UserEditForm
from apps.users.permissions import require_permission
from apps.users.selectors import company_users, list_users
from apps.users.services import UserActionError, create_user, limit_message, plan_limit_reached, set_user_active, update_user


@login_required
@require_permission('users.view_user')
def user_list(request):
    return render(request, 'users/user_list.html', {'users': list_users()})


@login_required
@require_permission('users.add_user')
def user_create(request):
    # Clic en Nuevo usuario por HTMX: modal si hay limite, si no abre el alta
    if request.method == 'GET' and request.htmx:
        if plan_limit_reached():
            return limit_blocked_response(request)
        return HttpResponseClientRedirect(reverse('users:user_create'))
    if plan_limit_reached():
        return limit_blocked_response(request)
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            try:
                create_user(user_form)
            except UserActionError:
                return limit_blocked_response(request)
            messages.success(request, 'Usuario creado correctamente.')
            return redirect_to_user_list(request)
        if request.htmx:
            return render(request, 'users/_user_form.html', {'form': user_form})
    else:
        user_form = UserCreateForm()
    return render(request, 'users/user_form.html', {'form': user_form})


@login_required
@require_permission('users.change_user')
def user_edit(request, user_id):
    user_to_edit = get_object_or_404(company_users(), pk=user_id)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_to_edit)
        if user_form.is_valid():
            update_user(user_form)
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect_to_user_list(request)
        if request.htmx:
            return render(request, 'users/_user_form.html', {'form': user_form})
    else:
        user_form = UserEditForm(instance=user_to_edit)
    return render(request, 'users/user_form.html', {'form': user_form})


@login_required
@require_permission('users.change_user')
def user_toggle_active(request, user_id):
    if request.method != 'POST':
        return redirect('users:user_list')
    user_to_change = get_object_or_404(company_users(), pk=user_id)
    try:
        set_user_active(user_to_change, not user_to_change.is_active)
    except UserActionError as action_error:
        if request.htmx:
            return toggle_row_response(request, user_to_change, str(action_error), 'error')
        messages.error(request, str(action_error))
        return redirect('users:user_list')
    if request.htmx:
        return toggle_row_response(request, user_to_change, 'Estado del usuario actualizado.', 'success')
    messages.success(request, 'Estado del usuario actualizado.')
    return redirect('users:user_list')


# Devuelve la fila actualizada y dispara el toast sin recargar
def toggle_row_response(request, user_row, toast_message, toast_level):
    response = render(request, 'users/_user_row.html', {'user_row': user_row})
    return trigger_client_event(response, 'show_toast', {'message': toast_message, 'level': toast_level})


# Vuelve al listado respetando si la peticion vino por HTMX
def redirect_to_user_list(request):
    if request.htmx:
        return HttpResponseClientRedirect(reverse('users:user_list'))
    return redirect('users:user_list')


# Bloqueo por limite del plan: con HTMX devuelve solo el modal, sin recargar
def limit_blocked_response(request):
    if request.htmx:
        return render(request, 'users/_limit_modal.html', {'limit_text': limit_message()})
    return render(request, 'users/user_form.html', {'form': UserCreateForm(), 'limit_reached': True, 'limit_text': limit_message()})
