from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from .mixins import LoggedOutRequiredMixin
from panel.models import Theme
from django.conf import settings

# Create your views here.
class AuthLoginView(LoggedOutRequiredMixin, TemplateView):
    template_name = "auth/login.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            context["success"] = False
            context["error"] = settings.INVALID_LOGIN_MESSAGE
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'Login'
        return context

class AuthRegisterView(LoggedOutRequiredMixin, TemplateView):
    template_name = "auth/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = 'Registration'
        return context
