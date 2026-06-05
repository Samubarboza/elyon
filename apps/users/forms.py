from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from apps.users.models import User


USER_FIELDS = ['username', 'first_name', 'last_name', 'email', 'phone', 'document', 'position']


class UserCreateForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = USER_FIELDS


class UserEditForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = USER_FIELDS
