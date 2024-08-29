from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Project


class ProjectPermissionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        # Get the project based on the URL parameter (assuming 'pk' is used)
        project = get_object_or_404(Project, pk=kwargs.get('id'))

        # Check if the user is the owner or a member of the project
        if project.owner != request.user and request.user not in project.members.all():
            raise PermissionDenied  # User is not authorized

        # Proceed with the view if the user has permission
        return super().dispatch(request, *args, **kwargs)