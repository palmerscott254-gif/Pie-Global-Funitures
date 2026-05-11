from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    Configuration class for the notifications app.
    Handles app initialization and signal registration.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'

    def ready(self):
        # Import signals when app is ready to ensure they are registered
        import apps.notifications.signals  # noqa
