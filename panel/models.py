from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class Theme(models.Model):
    name = models.CharField(max_length=255, unique=True)
    light_css = models.TextField(blank=True)
    dark_css = models.TextField(blank=True)
    default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.default:
            # Ensure only one Theme can be default
            Theme.objects.filter(default=True).update(default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.title()


# Signal to create a default theme after migrations
@receiver(post_migrate)
def create_default_theme(sender, **kwargs):
    if not Theme.objects.filter(default=True).exists():
        Theme.objects.create(
            name="Default",
            light_css=""":root {
  --body-bg: #f8f9fc;
  --body-bg-alt: #eaecf4;
  --bg-secondary: #0b4db0;
  --bg-primary: #9500ff;
  --bg-gradient: linear-gradient(100deg, var(--bg-primary) 0%, var(--bg-secondary) 50%);
  --bg-gradient-reverse: linear-gradient(100deg, var(--bg-secondary) 0%, var(--bg-primary) 50%);
  --bg-secondary-alt: #3F9900;
  --bg-primary-alt: #009999;
  --text-color: #5a5c69;
  --bg-color: #ffffff;
}""",
            dark_css=""":root {
  --body-bg: #333;
  --body-bg-alt: #333;
  --bg-secondary: #0b4db0;
  --bg-primary: #9500ff;
  --bg-gradient: linear-gradient(100deg, var(--bg-primary) 0%, var(--bg-secondary) 50%);
  --bg-gradient-reverse: linear-gradient(100deg, var(--bg-secondary) 0%, var(--bg-primary) 50%);
  --bg-primary-alt: #3F9900;
  --bg-secondary-alt: #009999;
  --text-color: #dfdfdf;
  --bg-color: #212121;
}""",
            default=True
        )
