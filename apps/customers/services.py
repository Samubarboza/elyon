import logging

logger = logging.getLogger('apps.customers')


def create_customer(customer_form):
    new_customer = customer_form.save()
    logger.info('Cliente creado: %s', new_customer.name)
    return new_customer


def update_customer(customer_form):
    updated_customer = customer_form.save()
    logger.info('Cliente actualizado: %s', updated_customer.name)
    return updated_customer


def set_customer_active(customer_to_change, is_active):
    customer_to_change.is_active = is_active
    customer_to_change.save(update_fields=['is_active'])
    logger.info('Estado de cliente actualizado: %s activo=%s', customer_to_change.name, is_active)
    return customer_to_change
