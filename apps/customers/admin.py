from django.contrib import admin

from apps.customers.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'document')

    # El cliente no se borra, solo se desactiva
    def has_delete_permission(self, request, customer=None):
        return False
