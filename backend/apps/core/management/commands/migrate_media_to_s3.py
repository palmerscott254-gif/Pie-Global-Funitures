"""
Management command to migrate local media files to S3.
Usage: python manage.py migrate_media_to_s3
"""
import os
import mimetypes
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import File
from storages.backends.s3boto3 import S3Boto3Storage


class Command(BaseCommand):
    help = 'Migrate all local media files to S3 bucket'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing files in S3',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        overwrite = options['overwrite']

        if not settings.USE_S3:
            self.stdout.write(
                self.style.ERROR('S3 is not enabled. Set USE_S3=True and configure AWS credentials.')
            )
            return

        # Initialize S3 storage
        try:
            s3_storage = S3Boto3Storage()
            self.stdout.write(
                self.style.SUCCESS(f'Connected to S3 bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to connect to S3: {str(e)}')
            )
            return

        # Get local media root
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            self.stdout.write(
                self.style.WARNING(f'Media directory does not exist: {media_root}')
            )
            return

        # Find all files in media directory
        all_files = []
        for root, dirs, files in os.walk(media_root):
            for filename in files:
                file_path = Path(root) / filename
                # Get relative path from MEDIA_ROOT
                relative_path = file_path.relative_to(media_root)
                all_files.append((file_path, str(relative_path).replace('\\', '/')))

        if not all_files:
            self.stdout.write(
                self.style.WARNING(f'No files found in {media_root}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Found {len(all_files)} files to migrate')
        )

        # Upload files
        uploaded = 0
        skipped = 0
        failed = 0

        for file_path, s3_key in all_files:
            try:
                # Check if file already exists in S3
                if not overwrite and s3_storage.exists(s3_key):
                    self.stdout.write(
                        self.style.WARNING(f'Skipped (exists): {s3_key}')
                    )
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        self.style.NOTICE(f'Would upload: {s3_key}')
                    )
                    uploaded += 1
                    continue

                # Upload file to S3
                with open(file_path, 'rb') as f:
                    # Guess content type
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    if not content_type:
                        content_type = 'application/octet-stream'

                    # Save to S3
                    s3_storage.save(s3_key, File(f))
                    self.stdout.write(
                        self.style.SUCCESS(f'Uploaded: {s3_key}')
                    )
                    uploaded += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload {s3_key}: {str(e)}')
                )
                failed += 1

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Migration Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  Uploaded: {uploaded}'))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  Skipped: {skipped}'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'  Failed: {failed}'))
        self.stdout.write(self.style.SUCCESS('='*50))

        if dry_run:
            self.stdout.write(
                self.style.NOTICE('\nThis was a dry run. Use without --dry-run to actually upload files.')
            )
