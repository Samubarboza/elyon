from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.users.forms import UserCreateForm, UserEditForm
from apps.users.selectors import company_users, list_users
from apps.users.services import UserActionError, create_user, set_user_active, update_user


@login_required
def user_list(request):
    return render(request, 'users/user_list.html', {'users': list_users()})


@login_required
def user_create(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            try:
                create_user(user_form)
            except UserActionError as action_error:
                messages.error(request, str(action_error))
                return render(request, 'users/user_form.html', {'form': user_form})
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('users:user_list')
    else:
        user_form = UserCreateForm()
    return render(request, 'users/user_form.html', {'form': user_form})


@login_required
def user_edit(request, user_id):
    user_to_edit = get_object_or_404(company_users(), pk=user_id)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user_to_edit)
        if user_form.is_valid():
            update_user(user_form)
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('users:user_list')
    else:
        user_form = UserEditForm(instance=user_to_edit)
    return render(request, 'users/user_form.html', {'form': user_form})


@login_required
def user_toggle_active(request, user_id):
    if request.method != 'POST':
        return redirect('users:user_list')
    user_to_change = get_object_or_404(company_users(), pk=user_id)
    try:
        set_user_active(user_to_change, not user_to_change.is_active)
    except UserActionError as action_error:
        messages.error(request, str(action_error))
        return redirect('users:user_list')
    messages.success(request, 'Estado del usuario actualizado.')
    return redirect('users:user_list')
