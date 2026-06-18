from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=150)
    document = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['document'],
                condition=~models.Q(document=''),
                name='customer_unique_document',
                violation_error_message='Ya existe un cliente con este documento.',
            ),
        ]

    def __str__(self):
        return self.name
