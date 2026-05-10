from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        """Register signal handlers for this app."""
        @receiver(post_migrate, sender=self)
        def create_default_admin_user(sender, **kwargs):
            """Auto-create dashboard admin user if env vars are set.
            
            Checks for:
            - DEFAULT_ADMIN_EMAIL
            - DEFAULT_ADMIN_PASSWORD
            - DEFAULT_ADMIN_NAME (optional, defaults to 'Dashboard Admin')
            
            Idempotent: skips if user already exists.
            """
            from apps.users.models import User
            
            admin_email = os.environ.get('DEFAULT_ADMIN_EMAIL')
            admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD')
            admin_name = os.environ.get('DEFAULT_ADMIN_NAME', 'Dashboard Admin')
            
            if not admin_email or not admin_password:
                return
            
            # Check if user already exists
            if User.objects.filter(email__iexact=admin_email).exists():
                return
            
            # Create admin user
            try:
                user = User(name=admin_name, email=admin_email, is_staff=True, is_superuser=True)
                user.set_password(admin_password)
                user.save()
                print(f'✓ Created dashboard admin user: {admin_email}')
            except Exception as e:
                print(f'✗ Failed to create admin user: {e}')

