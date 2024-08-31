from django.urls import path
from .views import *

urlpatterns = [
    path('admin/projects/', AdminProjectsView.as_view(), name="admin-projects"),
    path('admin/projects/view/<int:id>/', AdminProjectDetailView.as_view(), name="admin-project-detail"),
    path('admin/projects/edit/<int:id>/', AdminProjectEditView.as_view(), name="admin-project-edit"),
    path('admin/projects/tasks/<int:id>/', AdminTaskDetailView.as_view(), name="admin-task-detail"),

    path('projects/', ProjectsView.as_view(), name="projects"),
    path('projects/new/', ProjectCreateView.as_view(), name="project-create"),
    path('projects/view/<int:id>/', ProjectDetailView.as_view(), name="project-detail"),
    path('projects/view/<int:id>/settings/', ProjectSettingsView.as_view(), name="project-settings"),
]