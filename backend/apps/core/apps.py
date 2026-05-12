from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """Register automatic media cleanup for all file-bearing models."""
        from .s3_cleanup import register_all_media_model_cleanup

        # Register every installed model that contains ImageField or FileField.
        # This ensures future media models are covered automatically.
        register_all_media_model_cleanup()
