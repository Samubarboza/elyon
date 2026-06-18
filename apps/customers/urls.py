from django.urls import path

from apps.customers import views


app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:customer_id>/toggle-active/', views.customer_toggle_active, name='customer_toggle_active'),
]
