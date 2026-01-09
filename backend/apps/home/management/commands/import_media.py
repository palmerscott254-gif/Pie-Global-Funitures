import json
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from apps.home.models import SliderImage, HomeVideo


class Command(BaseCommand):
    help = 'Import SliderImage and HomeVideo records from exported JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default='media_export.json',
            help='Input JSON file path (default: media_export.json)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes'
        )
        parser.add_argument(
            '--sliders-only',
            action='store_true',
            help='Import only SliderImage records'
        )
        parser.add_argument(
            '--videos-only',
            action='store_true',
            help='Import only HomeVideo records'
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip records that already exist (by ID) instead of failing'
        )

    def handle(self, *args, **options):
        input_file = options['input']
        dry_run = options['dry_run']
        sliders_only = options['sliders_only']
        videos_only = options['videos_only']
        skip_duplicates = options['skip_duplicates']

        # Read JSON file
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {input_file}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in {input_file}'))
            return

        # Import SliderImage records
        if not videos_only and 'sliders' in data:
            self.stdout.write('\n--- Importing SliderImage records ---')
            for slider in data['sliders']:
                try:
                    if dry_run:
                        self.stdout.write(
                            f'[DRY RUN] Would create: SliderImage '
                            f'id={slider["id"]}, title={slider["title"]}, '
                            f'order={slider["order"]}, active={slider["active"]}'
                        )
                    else:
                        # Check if exists
                        if SliderImage.objects.filter(id=slider['id']).exists():
                            if skip_duplicates:
                                self.stdout.write(
                                    f'Skipping duplicate SliderImage id={slider["id"]}'
                                )
                                continue
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'SliderImage id={slider["id"]} already exists. '
                                        'Use --skip-duplicates to ignore.'
                                    )
                                )
                                continue
                        
                        SliderImage.objects.create(
                            id=slider['id'],
                            title=slider['title'],
                            image=slider.get('image'),
                            order=slider['order'],
                            active=slider['active'],
                            uploaded_at=slider['uploaded_at']
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created SliderImage id={slider["id"]}: {slider["title"]}'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating SliderImage: {e}')
                    )

        # Import HomeVideo records
        if not sliders_only and 'videos' in data:
            self.stdout.write('\n--- Importing HomeVideo records ---')
            for video in data['videos']:
                try:
                    if dry_run:
                        self.stdout.write(
                            f'[DRY RUN] Would create: HomeVideo '
                            f'id={video["id"]}, title={video["title"]}, '
                            f'active={video["active"]}'
                        )
                    else:
                        # Check if exists
                        if HomeVideo.objects.filter(id=video['id']).exists():
                            if skip_duplicates:
                                self.stdout.write(
                                    f'Skipping duplicate HomeVideo id={video["id"]}'
                                )
                                continue
                            else:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'HomeVideo id={video["id"]} already exists. '
                                        'Use --skip-duplicates to ignore.'
                                    )
                                )
                                continue
                        
                        HomeVideo.objects.create(
                            id=video['id'],
                            title=video['title'],
                            video=video.get('video'),
                            active=video['active'],
                            uploaded_at=video['uploaded_at']
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created HomeVideo id={video["id"]}: {video["title"]}'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating HomeVideo: {e}')
                    )

        mode_str = '[DRY RUN] ' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(f'\n{mode_str}Import complete!')
        )
        if not dry_run:
            self.stdout.write(self.style.WARNING(
                '\nNEXT STEPS:\n'
                '1. Commit and push this code to your repo\n'
                '2. Trigger a production redeploy\n'
                '3. On production, run: python manage.py sync_s3_to_db\n'
                '   (This will link S3 file paths to the imported records)'
            ))
