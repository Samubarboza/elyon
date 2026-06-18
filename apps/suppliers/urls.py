from django.urls import path

from apps.suppliers import views


app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('<int:supplier_id>/toggle-active/', views.supplier_toggle_active, name='supplier_toggle_active'),
]
