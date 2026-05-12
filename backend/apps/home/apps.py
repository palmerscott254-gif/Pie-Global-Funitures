from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.home'
    verbose_name = 'Home'

    def ready(self):
        # Cleanup signals are registered centrally by apps.core.apps.CoreConfig.
        # Keep this hook available for future home-specific startup logic.
        return
