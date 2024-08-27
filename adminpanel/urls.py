from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', AdminDashboardHome.as_view(), name="admin-dashboard-home"),
    path('admin/users/', AdminUsersView.as_view(), name="admin-users"),
    path('admin/users/edit/<int:id>/', AdminUserDetailView.as_view(), name="admin-user-detail"),
    path('admin/groups/', AdminGroupsView.as_view(), name="admin-groups"),
    path('admin/groups/edit/<int:id>/', AdminGroupDetailView.as_view(), name="admin-group-detail"),
    path('admin/groups/new/', AdminGroupCreateView.as_view(), name="admin-group-create"),
    path('admin/themes/', AdminThemesView.as_view(), name="admin-themes"),
    path('admin/themes/edit/<int:id>/', AdminThemeDetailView.as_view(), name='admin-theme-detail'),
]