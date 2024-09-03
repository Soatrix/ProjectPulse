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
from datetime import datetime
from .mixins import *

# Create your views here.
class AdminProjectsView(LoginRequiredMixin, TemplateView):
    template_name = "projectadmin/projects.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'All Projects'
        context["PROJECTS"] = Project.objects.all()
        return context
class AdminProjectDetailView(LoginRequiredMixin, TemplateView):
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
class AdminProjectEditView(LoginRequiredMixin, TemplateView):
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


class AdminTaskDetailView(LoginRequiredMixin, TemplateView):
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

class ProjectsView(LoginRequiredMixin, TemplateView):
    template_name = "projectpulse/projects.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'All Projects'
        context["PROJECTS"] = Project.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        )
        return context
class ProjectDetailView(LoginRequiredMixin, ProjectPermissionRequiredMixin, TemplateView):
    template_name = "projectpulse/project-detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["PAGE_TITLE"] = context["PROJECT"].name
        return context

class ProjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = "projectpulse/project-create.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = "Create Project"
        return context
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "create" in request.POST:
            requiredFields = ["name", "start_date"]
            fields = ["name", "start_date", "description", "logo"]
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
                project, created = Project.objects.get_or_create(
                    name=request.POST.get("name"),
                    description=request.POST.get("description"),
                    start_date=request.POST.get("start_date"),
                    owner=request.user,
                    logo=request.POST.get("logo")
                )
                if not created:
                    context["success"] = False
                    context["error"] = "A project with this name already exists, you can view it <a href=\"{% url 'project-detail' id=" + project.id + " %}\">here</a>."
                else:
                    return redirect("project-detail", id=project.id)

        return self.render_to_response(context)

class ProjectSettingsView(LoginRequiredMixin, ProjectPermissionRequiredMixin, TemplateView):
    template_name = "projectpulse/project-settings.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["PAGE_TITLE"] = context["PROJECT"].name + " Settings"
        return context
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "update-description" in request.POST:
            description = request.POST.get("description")
            if description != context["PROJECT"].description:
                context["PROJECT"].description = description
                context["PROJECT"].save()
                context["success"] = True
                context["message"] = "The projects description was successfully updated."
        elif "update-timeline" in request.POST:
            start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%d").date()
            end_date = request.POST.get("end_date")

            saveRequired = False
            if context["PROJECT"].start_date != start_date.isoformat():
                context["PROJECT"].start_date = start_date.isoformat()
                saveRequired = True

            if end_date != "":
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                if context["PROJECT"].end_date != end_date.isoformat():
                    context["PROJECT"].end_date = end_date.isoformat()
                    saveRequired = True

            if saveRequired:
                context["PROJECT"].save()
                context["success"] = True
                context["message"] = "The project's timeline was successfully updated."
        elif "mark-completed" in request.POST:
            context["PROJECT"].status = "completed"
            context["PROJECT"].save()
            context["success"] = True
            context["message"] = "The project was successfully marked as completed."
        elif "mark-cancelled" in request.POST:
            context["PROJECT"].status = "cancelled"
            context["PROJECT"].save()
            context["success"] = True
            context["message"] = "The project was successfully marked as cancelled."
        elif "mark-on-hold" in request.POST:
            context["PROJECT"].status = "on_hold"
            context["PROJECT"].save()
            context["success"] = True
            context["message"] = "The project was successfully marked as on hold."
        elif "mark-in-progress" in request.POST:
            context["PROJECT"].status = "in_progress"
            context["PROJECT"].save()
            context["success"] = True
            context["message"] = "The project was successfully marked as in progress."

        return self.render_to_response(context)

class ProjectTasksView(LoginRequiredMixin, ProjectPermissionRequiredMixin, TemplateView):
    template_name = "projectpulse/project-tasks.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["PAGE_TITLE"] = context["PROJECT"].name + " Tasks"
        return context

class ProjectTaskDetailView(LoginRequiredMixin, TemplateView):
    template_name = "projectpulse/task-detail.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["TASK"] = Task.objects.get(pk=self.kwargs.get("task"))
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
class ProjectTaskCreateView(LoginRequiredMixin, TemplateView):
    template_name = "projectpulse/task-create.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PROJECT"] = Project.objects.get(pk=self.kwargs.get("id"))
        context["STATUSES"] = Task.Status
        context["PAGE_TITLE"] = "New Task"
        return context
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if "create" in request.POST:
            requiredFields = ["name", "start_date"]
            fields = ["name", "start_date", "description", "end_date"]
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
            if not "error" in context:
                task, created = Task.objects.get_or_create(
                    project=context["PROJECT"],
                    name=request.POST.get("name"),
                    assignee=request.user,
                    description=request.POST.get("description"),
                    status="not_started",
                    start_date=request.POST.get("start_date")
                )
                if not created:
                    context["success"] = False
                    context["error"] = "A task with this name already exists. Please check your input and try again."
                else:
                    if "requirements" in request.POST:
                        requirementTasks = []
                        for requirement in request.POST.getlist("requirements"):
                            requirementTask = Task.objects.get(pk=int(requirement))
                            requirementTasks.append(requirementTask)
                        task.requirements.set(requirementTasks)
                        task.save()

                    end_date = request.POST.get("end_date")
                    if end_date != "":
                        task.end_date = end_date
                        task.save()
                    return redirect("project-task-detail", id=context["PROJECT"].id, task=task.id)

        return self.render_to_response(context)