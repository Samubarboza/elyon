import logging

logger = logging.getLogger('apps.suppliers')


def create_supplier(supplier_form):
    new_supplier = supplier_form.save()
    logger.info('Proveedor creado: %s', new_supplier.name)
    return new_supplier


def update_supplier(supplier_form):
    updated_supplier = supplier_form.save()
    logger.info('Proveedor actualizado: %s', updated_supplier.name)
    return updated_supplier


def set_supplier_active(supplier_to_change, is_active):
    supplier_to_change.is_active = is_active
    supplier_to_change.save(update_fields=['is_active'])
    logger.info('Estado de proveedor actualizado: %s activo=%s', supplier_to_change.name, is_active)
    return supplier_to_change
