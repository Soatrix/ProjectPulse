from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.text import slugify
from .models import *

# Create your views here.
class AdminProjectsView(TemplateView):
    template_name = "projectadmin/projects.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'All Projects'
        context["PROJECTS"] = Project.objects.all()
        return context
class AdminProjectDetailView(TemplateView):
    template_name = "projectadmin/project-detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["PAGE_TITLE"] = context["PROJECT"].name
        return context
class AdminProjectEditView(TemplateView):
    template_name = "projectadmin/project-edit.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["PAGE_TITLE"] = context["PROJECT"].name
        return context