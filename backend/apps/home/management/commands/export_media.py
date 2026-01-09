import json
import os
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from apps.home.models import SliderImage, HomeVideo


class Command(BaseCommand):
    help = 'Export SliderImage and HomeVideo records to JSON for transfer to production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='media_export.json',
            help='Output JSON file path (default: media_export.json)'
        )
        parser.add_argument(
            '--sliders-only',
            action='store_true',
            help='Export only SliderImage records'
        )
        parser.add_argument(
            '--videos-only',
            action='store_true',
            help='Export only HomeVideo records'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        sliders_only = options['sliders_only']
        videos_only = options['videos_only']

        data = {}

        # Export SliderImage records
        if not videos_only:
            sliders = SliderImage.objects.all().values(
                'id', 'title', 'order', 'active', 'uploaded_at'
            )
            data['sliders'] = list(sliders)
            self.stdout.write(
                self.style.SUCCESS(f'Exported {len(data["sliders"])} SliderImage records')
            )

        # Export HomeVideo records
        if not sliders_only:
            videos = HomeVideo.objects.all().values(
                'id', 'title', 'active', 'uploaded_at'
            )
            data['videos'] = list(videos)
            self.stdout.write(
                self.style.SUCCESS(f'Exported {len(data["videos"])} HomeVideo records')
            )

        # Write to file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Export complete: {output_file}')
        )
        self.stdout.write(self.style.WARNING(
            '\nNOTE: This export does NOT include image/video files.\n'
            'Files must already be synced to production S3 bucket.\n'
            'Use manage.py sync_s3_to_db on production to register files.'
        ))
