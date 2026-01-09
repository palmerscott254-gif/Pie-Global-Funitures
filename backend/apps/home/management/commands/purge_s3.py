"""
Management command to forcefully delete ALL media files from S3 bucket.
This removes files directly from S3, not from database records.
"""
import boto3
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Forcefully delete ALL media files from S3 bucket (home/ and products/)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if not settings.USE_S3:
            self.stdout.write(self.style.ERROR('S3 is not enabled'))
            return

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        bucket = settings.AWS_STORAGE_BUCKET_NAME
        prefixes = ['home/', 'products/']
        total_deleted = 0

        for prefix in prefixes:
            self.stdout.write(f'\nScanning S3: {prefix}...')
            
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
            
            files_to_delete = []
            for page in pages:
                if 'Contents' not in page:
                    continue
                for obj in page['Contents']:
                    files_to_delete.append(obj['Key'])
            
            if not files_to_delete:
                self.stdout.write(self.style.WARNING(f'  No files found in {prefix}'))
                continue
            
            self.stdout.write(f'  Found {len(files_to_delete)} files')
            
            for key in files_to_delete:
                if dry_run:
                    self.stdout.write(f'  Would delete: {key}')
                else:
                    try:
                        s3_client.delete_object(Bucket=bucket, Key=key)
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted: {key}'))
                        total_deleted += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Failed to delete {key}: {e}'))

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Would delete {len(files_to_delete)} files'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Deleted {total_deleted} files from S3'))
