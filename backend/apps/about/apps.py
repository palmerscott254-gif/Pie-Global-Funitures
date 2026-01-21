from django.apps import AppConfig


class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.about'
    
    # NOTE: Do not access database in ready() - it runs before migrations
    # Instead, create a data migration or management command to initialize default data
