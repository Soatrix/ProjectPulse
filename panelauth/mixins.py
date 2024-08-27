from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoggedOutRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect(settings.LOGIN_REDIRECT_URL)  # Redirect to your desired URL if the user is logged in
