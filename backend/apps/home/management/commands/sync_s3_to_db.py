"""
Management command to sync S3 files with database records.
This creates database entries for files that exist in S3 but not in the database.
"""
import boto3
from botocore.config import Config
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.home.models import SliderImage, HomeVideo


class Command(BaseCommand):
    help = 'Sync S3 bucket files with database records for SliderImages and HomeVideos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Remove database records for files that no longer exist in S3',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clean = options['clean']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Initialize S3 client
        try:
            s3_config = Config(signature_version='s3v4', s3={'addressing_style': 'virtual'})
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
                config=s3_config,
            )
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            self.stdout.write(f'Connected to S3 bucket: {bucket_name}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to connect to S3: {e}'))
            return

        # Sync slider images
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Syncing Slider Images...')
        self.stdout.write('='*50)
        self._sync_sliders(s3_client, bucket_name, dry_run, clean)

        # Sync home videos
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Syncing Home Videos...')
        self.stdout.write('='*50)
        self._sync_videos(s3_client, bucket_name, dry_run, clean)

        self.stdout.write(self.style.SUCCESS('\n✓ Sync completed!'))

    def _sync_sliders(self, s3_client, bucket_name, dry_run, clean):
        """Sync slider images from S3 to database"""
        prefix = 'home/sliders/'
        
        # Get all files in S3
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            s3_files = set()
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    # Skip directory markers
                    if not key.endswith('/'):
                        s3_files.add(key)
            
            self.stdout.write(f'Found {len(s3_files)} slider images in S3')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error listing S3 files: {e}'))
            return

        # Get existing database records
        existing_sliders = {img.image.name: img for img in SliderImage.objects.all()}
        self.stdout.write(f'Found {len(existing_sliders)} slider images in database')

        # Create missing database records
        created_count = 0
        for s3_key in s3_files:
            if s3_key not in existing_sliders:
                filename = s3_key.split('/')[-1]
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'Would create: {s3_key}'))
                else:
                    SliderImage.objects.create(
                        title=f'Slider {filename}',
                        image=s3_key,
                        active=True,
                        order=0
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created: {s3_key}'))
                created_count += 1

        # Clean up database records for missing S3 files
        removed_count = 0
        if clean:
            for db_key, slider_obj in existing_sliders.items():
                if db_key not in s3_files:
                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'Would remove: {db_key} (ID: {slider_obj.id})'))
                    else:
                        slider_obj.delete()
                        self.stdout.write(self.style.ERROR(f'Removed: {db_key} (ID: {slider_obj.id})'))
                    removed_count += 1

        self.stdout.write(f'\nSlider Summary: Created {created_count}, Removed {removed_count}')

    def _sync_videos(self, s3_client, bucket_name, dry_run, clean):
        """Sync home videos from S3 to database"""
        prefix = 'home/videos/'
        
        # Get all files in S3
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            s3_files = set()
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    # Skip directory markers
                    if not key.endswith('/'):
                        s3_files.add(key)
            
            self.stdout.write(f'Found {len(s3_files)} videos in S3')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error listing S3 files: {e}'))
            return

        # Get existing database records
        existing_videos = {vid.video.name: vid for vid in HomeVideo.objects.all()}
        self.stdout.write(f'Found {len(existing_videos)} videos in database')

        # Create missing database records
        created_count = 0
        for s3_key in s3_files:
            if s3_key not in existing_videos:
                filename = s3_key.split('/')[-1]
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'Would create: {s3_key}'))
                else:
                    HomeVideo.objects.create(
                        title=f'Video {filename}',
                        video=s3_key,
                        active=True
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created: {s3_key}'))
                created_count += 1

        # Clean up database records for missing S3 files
        removed_count = 0
        if clean:
            for db_key, video_obj in existing_videos.items():
                if db_key not in s3_files:
                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'Would remove: {db_key} (ID: {video_obj.id})'))
                    else:
                        video_obj.delete()
                        self.stdout.write(self.style.ERROR(f'Removed: {db_key} (ID: {video_obj.id})'))
                    removed_count += 1

        self.stdout.write(f'\nVideo Summary: Created {created_count}, Removed {removed_count}')
