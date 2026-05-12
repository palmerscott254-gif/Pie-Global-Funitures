from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Products'

    def ready(self):
        # Cleanup signals are registered centrally by apps.core.apps.CoreConfig.
        # Keep this hook available for future product-specific startup logic.
        return
