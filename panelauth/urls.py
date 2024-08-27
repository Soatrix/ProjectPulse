from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('auth/login/', AuthLoginView.as_view(), name="auth-login"),
    path('auth/logout/', auth_views.LogoutView.as_view(), name="auth-logout"),
    path('auth/register/', AuthRegisterView.as_view(), name="auth-register"),
]