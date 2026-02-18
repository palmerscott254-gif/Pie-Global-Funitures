"""
Management command to ensure baseline products exist (safe for repeated runs).
This is a wrapper around fix_production_products that always uses safe mode.

Usage: python manage.py ensure_products
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Ensure baseline products exist without overwriting existing ones'

    def handle(self, *args, **options):
        self.stdout.write('Ensuring baseline products exist (safe mode)...')
        call_command('fix_production_products', '--safe-mode')
