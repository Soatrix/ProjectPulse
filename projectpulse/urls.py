from django.urls import path
from .views import *

urlpatterns = [
    path('projects/', AdminProjectsView.as_view(), name="admin-projects"),
    path('projects/edit/<int:id>/', AdminProjectDetailView.as_view(), name="admin-project-detail"),
]