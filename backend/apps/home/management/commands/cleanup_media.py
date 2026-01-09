"""
Management command to clean up all media files from S3 and database.
Useful for removing all sliders, videos, and product images.
"""
import boto3
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.home.models import SliderImage, HomeVideo
from apps.products.models import Product


class Command(BaseCommand):
    help = 'Delete all media files from S3 and remove corresponding database records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--sliders-only',
            action='store_true',
            help='Delete only slider images',
        )
        parser.add_argument(
            '--videos-only',
            action='store_true',
            help='Delete only home videos',
        )
        parser.add_argument(
            '--products-only',
            action='store_true',
            help='Delete only product images',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        sliders_only = options['sliders_only']
        videos_only = options['videos_only']
        products_only = options['products_only']

        # If none specified, do all
        do_all = not (sliders_only or videos_only or products_only)

        if settings.USE_S3:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
        else:
            s3_client = None

        # Delete sliders
        if do_all or sliders_only:
            self._delete_sliders(s3_client, dry_run)

        # Delete videos
        if do_all or videos_only:
            self._delete_videos(s3_client, dry_run)

        # Delete product images
        if do_all or products_only:
            self._delete_product_images(s3_client, dry_run)

        self.stdout.write(self.style.SUCCESS('\n✓ Cleanup complete!'))

    def _delete_sliders(self, s3_client, dry_run):
        """Delete all slider images from S3 and database."""
        sliders = SliderImage.objects.all()
        count = sliders.count()

        if count == 0:
            self.stdout.write(self.style.WARNING('No slider images to delete'))
            return

        self.stdout.write(f'\nSlider Images: {count} found')

        for slider in sliders:
            s3_key = slider.image.name
            slider_id = slider.id

            if s3_client:
                try:
                    if dry_run:
                        self.stdout.write(f'  Would delete S3: {s3_key}')
                    else:
                        s3_client.delete_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=s3_key,
                        )
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted S3: {s3_key}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed S3 delete {s3_key}: {e}'))

            if dry_run:
                self.stdout.write(f'  Would delete DB: SliderImage ID {slider_id}')
            else:
                slider.delete()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted DB: SliderImage ID {slider_id}'))

    def _delete_videos(self, s3_client, dry_run):
        """Delete all home videos from S3 and database."""
        videos = HomeVideo.objects.all()
        count = videos.count()

        if count == 0:
            self.stdout.write(self.style.WARNING('No home videos to delete'))
            return

        self.stdout.write(f'\nHome Videos: {count} found')

        for video in videos:
            s3_key = video.video.name
            video_id = video.id

            if s3_client:
                try:
                    if dry_run:
                        self.stdout.write(f'  Would delete S3: {s3_key}')
                    else:
                        s3_client.delete_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=s3_key,
                        )
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted S3: {s3_key}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed S3 delete {s3_key}: {e}'))

            if dry_run:
                self.stdout.write(f'  Would delete DB: HomeVideo ID {video_id}')
            else:
                video.delete()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted DB: HomeVideo ID {video_id}'))

    def _delete_product_images(self, s3_client, dry_run):
        """Delete all product main images from S3 and database."""
        products = Product.objects.filter(main_image__isnull=False).exclude(main_image='')
        count = products.count()

        if count == 0:
            self.stdout.write(self.style.WARNING('No product images to delete'))
            return

        self.stdout.write(f'\nProduct Images: {count} found')

        for product in products:
            if not product.main_image or not product.main_image.name:
                continue

            s3_key = product.main_image.name
            product_id = product.id
            product_name = product.name

            if s3_client:
                try:
                    if dry_run:
                        self.stdout.write(f'  Would delete S3: {s3_key}')
                    else:
                        s3_client.delete_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=s3_key,
                        )
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Deleted S3: {s3_key}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed S3 delete {s3_key}: {e}'))

            if dry_run:
                self.stdout.write(f'  Would clear DB: Product ID {product_id} ({product_name})')
            else:
                product.main_image.delete(save=False)
                product.save()
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Cleared DB: Product ID {product_id} ({product_name})'
                ))
