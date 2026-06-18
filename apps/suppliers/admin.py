from django.contrib import admin

from apps.suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'document')

    # El proveedor no se borra, solo se desactiva
    def has_delete_permission(self, request, supplier=None):
        return False
