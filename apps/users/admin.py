from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.password_validation import password_validators_help_text_html

from apps.users.models import Company, Plan, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_main_admin', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos de la empresa', {'fields': ('is_main_admin', 'phone', 'document', 'position')}),
    )

    # Mostrar las reglas de la contrasena como ayuda al crear el usuario
    def get_form(self, request, user_to_edit=None, **kwargs):
        user_form = super().get_form(request, user_to_edit, **kwargs)
        if 'password1' in user_form.base_fields:
            user_form.base_fields['password1'].help_text = password_validators_help_text_html()
        return user_form


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_users')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan')

    # La empresa es unica: no se crea otra ni se elimina
    def has_add_permission(self, request):
        return not Company.objects.exists()

    def has_delete_permission(self, request, company=None):
        return False
