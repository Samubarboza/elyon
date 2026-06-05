from django.contrib.auth.models import AbstractUser
from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_users = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'plan'
        verbose_name_plural = 'planes'

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=150)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='companies')

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresa'

    # La empresa es un unico registro (singleton): siempre pk=1
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def max_users(self):
        return self.plan.max_users

    @classmethod
    def get_config(cls):
        return cls.objects.select_related('plan').get(pk=1)

    def __str__(self):
        return self.name


class User(AbstractUser):
    is_main_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=30, blank=True)
    document = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=50, blank=True)
