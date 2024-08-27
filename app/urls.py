"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.apps import apps
from importlib import import_module
from django.conf import settings

urlpatterns = [
    path('djadmin/', admin.site.urls),
]

for app_config in apps.get_app_configs():
    try:
        # Try to import the app's urls module
        if app_config.name != ("django.contrib.auth"):
            module = import_module(f'{app_config.name}.urls')
            # If the import succeeds, include the URLs
            urlpatterns.append(path(f'', include(f'{app_config.name}.urls')))
    except ModuleNotFoundError:
        # If there's no urls module, skip to the next app
        pass
