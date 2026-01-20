"""
Management command to deduplicate SliderImage records
Removes duplicate entries while preserving the ones with most metadata
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.home.models import SliderImage, HomeVideo


class Command(BaseCommand):
    help = 'Remove duplicate SliderImage and HomeVideo records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be removed without actually removing',
        )
        parser.add_argument(
            '--sliders-only',
            action='store_true',
            help='Only deduplicate slider images',
        )
        parser.add_argument(
            '--videos-only',
            action='store_true',
            help='Only deduplicate videos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        sliders_only = options['sliders_only']
        videos_only = options['videos_only']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))

        # Deduplicate sliders
        if not videos_only:
            self._deduplicate_sliders(dry_run)

        # Deduplicate videos
        if not sliders_only:
            self._deduplicate_videos(dry_run)

        self.stdout.write(self.style.SUCCESS('\n✓ Deduplication complete!'))

    def _deduplicate_sliders(self, dry_run):
        """Remove duplicate slider images, keeping the one with most metadata"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Deduplicating SliderImages...')
        self.stdout.write('='*50 + '\n')

        # Group by image path
        image_groups = {}
        for slider in SliderImage.objects.all():
            image_path = slider.image.name if slider.image else f'empty_{slider.id}'
            if image_path not in image_groups:
                image_groups[image_path] = []
            image_groups[image_path].append(slider)

        total_removed = 0

        for image_path, sliders in image_groups.items():
            if len(sliders) > 1:
                self.stdout.write(f'Found {len(sliders)} duplicates for: {image_path}')

                # Keep the one with most metadata (title, active, oldest)
                def priority(slider):
                    score = 0
                    if slider.title:
                        score += 10
                    if slider.active:
                        score += 5
                    # Prefer older records
                    score -= (slider.id / 1000)
                    return score

                sliders_sorted = sorted(sliders, key=priority, reverse=True)
                keeper = sliders_sorted[0]
                removals = sliders_sorted[1:]

                self.stdout.write(f'  → Keeping ID {keeper.id} (title="{keeper.title}", active={keeper.active})')

                for removal in removals:
                    self.stdout.write(f'    ✗ Removing ID {removal.id} (title="{removal.title}", active={removal.active})')

                    if not dry_run:
                        removal.delete()
                        total_removed += 1

        self.stdout.write(self.style.SUCCESS(f'Removed {total_removed} duplicate SliderImages'))

    def _deduplicate_videos(self, dry_run):
        """Remove duplicate videos"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Deduplicating HomeVideos...')
        self.stdout.write('='*50 + '\n')

        # Group by video path
        video_groups = {}
        for video in HomeVideo.objects.all():
            video_path = video.video.name if video.video else f'empty_{video.id}'
            if video_path not in video_groups:
                video_groups[video_path] = []
            video_groups[video_path].append(video)

        total_removed = 0

        for video_path, videos in video_groups.items():
            if len(videos) > 1:
                self.stdout.write(f'Found {len(videos)} duplicates for: {video_path}')

                # Keep the one with most metadata
                def priority(v):
                    score = 0
                    if v.title:
                        score += 10
                    if v.active:
                        score += 5
                    score -= (v.id / 1000)
                    return score

                videos_sorted = sorted(videos, key=priority, reverse=True)
                keeper = videos_sorted[0]
                removals = videos_sorted[1:]

                self.stdout.write(f'  → Keeping ID {keeper.id} (title="{keeper.title}", active={keeper.active})')

                for removal in removals:
                    self.stdout.write(f'    ✗ Removing ID {removal.id} (title="{removal.title}", active={removal.active})')

                    if not dry_run:
                        removal.delete()
                        total_removed += 1

        self.stdout.write(self.style.SUCCESS(f'Removed {total_removed} duplicate HomeVideos'))
