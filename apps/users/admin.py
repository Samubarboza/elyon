from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import Company, Plan, User


admin.site.register(User, UserAdmin)


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
