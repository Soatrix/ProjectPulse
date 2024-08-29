from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.text import slugify
from django.db.models import Q
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

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "delete" in request.POST:
            context["PROJECT"].delete()
            return redirect("admin-projects")

        return self.render_to_response(context)
class AdminProjectEditView(TemplateView):
    template_name = "projectadmin/project-edit.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["STATUSES"] = Project.Status
        context["PAGE_TITLE"] = context["PROJECT"].name
        return context
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "update" in request.POST:
            requiredFields = ["name", "status", "start_date"]
            fields = ["name", "status", "start_date", "end_date", "description"]
            started = False
            for field in fields:
                if field not in request.POST and field in requiredFields:
                    if not started:
                        started = True
                        context["error"] = "<ul>"
                    context["error"] = context["error"] + f"<li>{field} is required."
                elif field in request.POST and field in requiredFields and request.POST.get(field) == "":
                    if not started:
                        context["error"] = "<ul>"
                        started = True
                    context["error"] = context["error"] + f"<li>The field \"" + field.replace("-", " ").replace("_", " ").title() + "\" is required.</li>"
            if started:
                context["error"] = context["error"] + "</ul>"
            saveRequired = False
            if not "error" in context:
                for field in fields:
                    setattr(context["PROJECT"], field, request.POST.get(field))
                    saveRequired = True
            if saveRequired:
                context["PROJECT"].save()
                context["success"] = True

        return self.render_to_response(context)


class AdminTaskDetailView(TemplateView):
    template_name = "projectadmin/task-detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["TASK"] = Task.objects.get(pk=self.kwargs.get("id"))
        context["STATUSES"] = Task.Status
        context["PAGE_TITLE"] = context["TASK"].name
        return context
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "mark-complete" in request.POST:
            context["TASK"].status = "completed"
            context["TASK"].save()
            context["success"] = True
            context["message"] = "The task was successfully marked as completed."
        elif "mark-started" in request.POST:
            if context["TASK"].status == "completed" or context["TASK"].status == "cancelled":
                context["message"] = "The task was successfully reopened."
            else:
                context["context"] = "The task was successfully marked as in progress."
            context["TASK"].status = "in_progress"
            context["TASK"].save()
            context["success"] = True

        return self.render_to_response(context)

class ProjectsView(TemplateView):
    template_name = "projectpulse/projects.html"
    def get_context_data(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'All Projects'
        context["PROJECTS"] = Project.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        )
        return context