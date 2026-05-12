from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Assigns `role` values to existing users: superusers -> super_admin, "
        "staff -> staff_admin. By default runs as a dry-run; pass --apply to save."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually persist role changes to the database (default: dry-run).",
        )

    def handle(self, *args, **options):
        apply_changes = options.get("apply", False)

        from apps.users.models import User

        users = User.objects.all()
        total = users.count()
        changed = 0
        changes = []

        for u in users:
            desired = None
            if u.is_superuser:
                desired = User.ROLE_SUPER
            elif u.is_staff:
                desired = User.ROLE_STAFF

            if desired and u.role != desired:
                changes.append((str(u.id), u.email, u.role, desired))
                if apply_changes:
                    u.role = desired
                    u.save(update_fields=["role"])
                changed += 1

        self.stdout.write(self.style.NOTICE(f"Total users inspected: {total}"))
        self.stdout.write(self.style.SUCCESS(f"Pending role changes: {len(changes)}"))

        if changes:
            for uid, email, old, new in changes:
                self.stdout.write(f" - {email} ({uid}): {old} -> {new}")

        if apply_changes:
            self.stdout.write(self.style.SUCCESS(f"Applied {changed} role changes."))
        else:
            self.stdout.write(self.style.WARNING("Dry-run complete. Rerun with --apply to persist changes."))
