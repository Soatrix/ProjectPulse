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
import json

# Create your views here.
class Dashboard404View(TemplateView):
    template_name = "404.html"

class DashboardHome(TemplateView):
    template_name = "panel/dashboard.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'Dashboard'
        return context

class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "panel/account.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PAGE_TITLE'] = 'Manage Account'
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if "password" in request.POST and "new-password" in request.POST and "new-password-confirm" in request.POST:
            password = request.POST["password"]
            new_password = request.POST["new-password"]
            new_password_confirm = request.POST["new-password-confirm"]
            if password != "" and new_password != "" and new_password_confirm != "":
                # Verify Password
                if self.request.user.check_password(password):
                    # Verify Matching Passwords
                    if new_password == new_password_confirm:
                        self.request.user.set_password(new_password)
                        self.request.user.save()
                        context["password_success"] = True
                    else:
                        context["password_success"] = False
                        context["password_error"] = "Passwords do not match. Please check your input and try again."
                else:
                    context["password_success"] = False
                    context["password_error"] = "Your current password did not match. Please check your input and try again."
            else:
                context["password_success"] = False
                context["password_error"] = "All fields are required."
        elif "email" in request.POST and "email-confirm" in request.POST:
            email = request.POST["email"]
            email_confirm = request.POST["email-confirm"]
            if email != "" and email_confirm != "":
                # Validate Emails
                if email == email_confirm:
                    try:
                        validate_email(email)
                        validate_email(email_confirm)
                        context["email_success"] = True
                    except ValidationError:
                        context["email_success"] = False
                        context["email_error"] = "Email address is invalid. Please check your input and try again."
                else:
                    context["email_success"] = False
                    context["email_error"] = "Email addresses do not match. Please check your input and try again."
            else:
                context["email_success"] = False
                context["email_error"] = "All fields are required."
            if context["email_success"]:
                self.request.user.email = email
                self.request.user.save()
        elif "theme" in request.POST:
            darkMode = "dark-mode" in request.POST
            themeID = int(request.POST.get("theme"))
            theme = Theme.objects.get(pk=themeID)
            try:
                profile = UserProfile.objects.get(user=request.user)
                profile.theme = theme
                profile.dark_mode = darkMode
                profile.save()
            except ObjectDoesNotExist:
                profile = UserProfile.objects.create(user=request.user, theme=theme, dark_mode=darkMode)
                profile.save()

        return self.render_to_response(context)