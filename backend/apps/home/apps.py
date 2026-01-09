from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home'
    verbose_name = 'Home'

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
