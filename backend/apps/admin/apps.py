from django.apps import AppConfig


class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin'
    # Use a custom label to avoid colliding with Django's builtin 'admin' app
    label = 'pgf_admin'
    verbose_name = 'Admin Dashboard'
