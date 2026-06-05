from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.users import views


app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('users:password_change_done')), name='password_change',),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
]
