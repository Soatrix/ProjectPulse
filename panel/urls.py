from django.urls import path
from .views import *

urlpatterns = [
    path('', DashboardHome.as_view(), name="dashboard-home"),

    path('account/', AccountView.as_view(), name="account-home"),
]