from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "active_project":
            # Limit the queryset for the active_project field
            user = request.user
            kwargs["queryset"] = Project.objects.filter(
                models.Q(owner=user) | models.Q(members=user)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name",)