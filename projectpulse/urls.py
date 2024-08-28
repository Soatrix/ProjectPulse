from django.urls import path
from .views import *

urlpatterns = [
    path('admin/projects/', AdminProjectsView.as_view(), name="admin-projects"),
    path('admin/projects/view/<int:id>/', AdminProjectDetailView.as_view(), name="admin-project-detail"),
    path('admin/projects/edit/<int:id>/', AdminProjectEditView.as_view(), name="admin-project-edit"),
    path('admin/projects/tasks/<int:id>/', AdminTaskDetailView.as_view(), name="admin-task-detail"),
]