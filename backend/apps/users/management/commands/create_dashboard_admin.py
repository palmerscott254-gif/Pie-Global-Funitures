from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.apps import apps


class Command(BaseCommand):
    help = "Create a dashboard admin user in the users table"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email for the admin user")
        parser.add_argument("--name", default="Dashboard Admin", help="Name for the admin user")
        parser.add_argument("--password", default=None, help="Password for the admin user (auto-generated if omitted)")

    def handle(self, *args, **options):
        User = apps.get_model("users", "User")
        email = options.get("email")
        name = options.get("name")
        password = options.get("password") or get_random_string(12)

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User with email {email} already exists."))
            return

        user = User(name=name, email=email, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Created dashboard admin user: {email}"))
        self.stdout.write(f"Password: {password}")
