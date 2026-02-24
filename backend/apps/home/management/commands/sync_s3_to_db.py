"""
Management command to sync S3 files with database records.
This creates database entries for files that exist in S3 but not in the database.
"""
import boto3
from botocore.config import Config
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.home.models import SliderImage, HomeVideo
from apps.products.models import Product


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
            # Trim credentials to remove whitespace that might cause signature issues
            access_key = str(settings.AWS_ACCESS_KEY_ID).strip()
            secret_key = str(settings.AWS_SECRET_ACCESS_KEY).strip()
            bucket_name = str(settings.AWS_STORAGE_BUCKET_NAME).strip()
            region = str(settings.AWS_S3_REGION_NAME).strip()
            
            # Validate credentials are present
            if not access_key or not secret_key:
                self.stdout.write(self.style.ERROR('AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in environment.'))
                return
            
            self.stdout.write(f'Using region: {region}, bucket: {bucket_name}')
            self.stdout.write(f'Access key: {access_key[:8]}... (length: {len(access_key)})')
            
            s3_config = Config(signature_version='s3v4', s3={'addressing_style': 'virtual'})
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                config=s3_config,
            )
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

        # Sync products
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Syncing Products...')
        self.stdout.write('='*50)
        self._sync_products(s3_client, bucket_name, dry_run, clean)

        self.stdout.write(self.style.SUCCESS('\n✓ Sync completed!'))

    def _sync_sliders(self, s3_client, bucket_name, dry_run, clean):
        """Sync slider images from S3 to database"""
        prefix = 'media/home/sliders/'
        
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

        # Get existing database records - normalize paths for comparison
        existing_sliders = {}
        for img in SliderImage.objects.all():
            if img.image:
                # Store by both raw and normalized paths to handle format variations
                existing_sliders[str(img.image.name)] = img
                # Also normalize the path
                normalized = self._normalize_s3_key(str(img.image.name))
                existing_sliders[normalized] = img
                existing_sliders[f'media/{normalized}'] = img  # Also store with media/ prefix
        
        empty_sliders = list(SliderImage.objects.filter(image='') | SliderImage.objects.filter(image__isnull=True))
        self.stdout.write(f'Found {len(set(existing_sliders.values()))} slider images in database with files')
        self.stdout.write(f'Found {len(empty_sliders)} slider images in database WITHOUT files')

        # Update empty database records with S3 files
        updated_count = 0
        processed = set()
        for s3_key in list(s3_files):
            # Try to match with empty sliders first (by order)
            if empty_sliders and s3_key not in processed:
                slider = empty_sliders.pop(0)
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'Would update ID {slider.id}: {s3_key}'))
                else:
                    slider.image = s3_key
                    slider.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated ID {slider.id}: {s3_key}'))
                updated_count += 1
                processed.add(s3_key)
                # Update the existence dict
                existing_sliders[s3_key] = slider
                existing_sliders[self._normalize_s3_key(s3_key)] = slider

        # Create missing database records for remaining S3 files
        created_count = 0
        for s3_key in s3_files:
            if s3_key not in processed:
                # Check multiple formats to see if it exists
                normalized = self._normalize_s3_key(s3_key)
                exists = (s3_key in existing_sliders or 
                         normalized in existing_sliders or 
                         f'media/{normalized}' in existing_sliders)
                
                if not exists:
                    # Final check: query database directly with both formats
                    try:
                        SliderImage.objects.get(image=s3_key)
                        self.stdout.write(self.style.WARNING(f'Already exists: {s3_key}'))
                        created_count += 0
                        continue
                    except SliderImage.DoesNotExist:
                        pass
                    
                    filename = s3_key.split('/')[-1]
                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'Would create: {s3_key}'))
                    else:
                        try:
                            slider = SliderImage.objects.create(
                                image=s3_key,
                                title=f'Slider {filename}',
                                active=True,
                                order=0
                            )
                            self.stdout.write(self.style.SUCCESS(f'Created: {s3_key}'))
                            created_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Failed to create slider for {s3_key}: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Already exists: {s3_key}'))

        # Clean up database records for missing S3 files
        removed_count = 0
        if clean:
            for db_record in SliderImage.objects.all():
                if db_record.image:
                    found = False
                    db_path = str(db_record.image.name)
                    for s3_key in s3_files:
                        if db_path == s3_key or self._normalize_s3_key(db_path) == self._normalize_s3_key(s3_key):
                            found = True
                            break
                    if not found:
                        if dry_run:
                            self.stdout.write(self.style.WARNING(f'Would remove: {db_path} (ID: {db_record.id})'))
                        else:
                            db_record.delete()
                            self.stdout.write(self.style.ERROR(f'Removed: {db_path} (ID: {db_record.id})'))
                        removed_count += 1

        self.stdout.write(f'\nSlider Summary: Updated {updated_count}, Created {created_count}, Removed {removed_count}')

    def _sync_videos(self, s3_client, bucket_name, dry_run, clean):
        """Sync home videos from S3 to database"""
        prefix = 'media/home/videos/'
        
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

        # Get existing database records - normalize paths for comparison
        existing_videos = {}
        for vid in HomeVideo.objects.all():
            if vid.video:
                # Store by both raw and normalized paths to handle format variations
                existing_videos[str(vid.video.name)] = vid
                normalized = self._normalize_s3_key(str(vid.video.name))
                existing_videos[normalized] = vid
                existing_videos[f'media/{normalized}'] = vid  # Also store with media/ prefix
        
        empty_videos = list(HomeVideo.objects.filter(video='') | HomeVideo.objects.filter(video__isnull=True))
        self.stdout.write(f'Found {len(set(existing_videos.values()))} videos in database with files')
        self.stdout.write(f'Found {len(empty_videos)} videos in database WITHOUT files')

        # Update empty database records with S3 files
        updated_count = 0
        processed = set()
        for s3_key in list(s3_files):
            # Try to match with empty videos first
            if empty_videos and s3_key not in processed:
                video = empty_videos.pop(0)
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'Would update ID {video.id}: {s3_key}'))
                else:
                    video.video = s3_key
                    video.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated ID {video.id}: {s3_key}'))
                updated_count += 1
                processed.add(s3_key)
                # Update the existence dict
                existing_videos[s3_key] = video
                existing_videos[self._normalize_s3_key(s3_key)] = video

        # Create missing database records for remaining S3 files
        created_count = 0
        for s3_key in s3_files:
            if s3_key not in processed:
                # Check multiple formats to see if it exists
                normalized = self._normalize_s3_key(s3_key)
                exists = (s3_key in existing_videos or 
                         normalized in existing_videos or 
                         f'media/{normalized}' in existing_videos)
                
                if not exists:
                    # Final check: query database directly with both formats
                    try:
                        HomeVideo.objects.get(video=s3_key)
                        self.stdout.write(self.style.WARNING(f'Already exists: {s3_key}'))
                        created_count += 0
                        continue
                    except HomeVideo.DoesNotExist:
                        pass
                    
                    filename = s3_key.split('/')[-1]
                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'Would create: {s3_key}'))
                    else:
                        try:
                            video = HomeVideo.objects.create(
                                video=s3_key,
                                title=f'Video {filename}',
                                active=True
                            )
                            self.stdout.write(self.style.SUCCESS(f'Created: {s3_key}'))
                            created_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Failed to create video for {s3_key}: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Already exists: {s3_key}'))

        # Clean up database records for missing S3 files
        removed_count = 0
        if clean:
            for db_record in HomeVideo.objects.all():
                if db_record.video:
                    found = False
                    db_path = str(db_record.video.name)
                    for s3_key in s3_files:
                        if db_path == s3_key or self._normalize_s3_key(db_path) == self._normalize_s3_key(s3_key):
                            found = True
                            break
                    if not found:
                        if dry_run:
                            self.stdout.write(self.style.WARNING(f'Would remove: {db_path} (ID: {db_record.id})'))
                        else:
                            db_record.delete()
                            self.stdout.write(self.style.ERROR(f'Removed: {db_path} (ID: {db_record.id})'))
                        removed_count += 1

        self.stdout.write(f'\nVideo Summary: Updated {updated_count}, Created {created_count}, Removed {removed_count}')

    def _sync_products(self, s3_client, bucket_name, dry_run, clean):
        """Sync product main images from S3 to database"""
        prefix = 'media/products/main/'

        # Get all files in S3
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            s3_files = set()

            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if not key.endswith('/'):
                        s3_files.add(key)

            self.stdout.write(f'Found {len(s3_files)} product images in S3')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error listing S3 product files: {e}'))
            return

        # Normalize S3 keys so we avoid double "media/" prefixes when saving to storage
        normalized_s3_files = {self._normalize_s3_key(key) for key in s3_files}

        # Get existing database records - normalize paths for comparison
        existing_products = {}
        for prod in Product.objects.all():
            if prod.main_image:
                # Store by both raw and normalized paths to handle format variations
                existing_products[str(prod.main_image.name)] = prod
                normalized = self._normalize_s3_key(str(prod.main_image.name))
                existing_products[normalized] = prod
                existing_products[f'media/{normalized}'] = prod  # Also store with media/ prefix
        
        empty_products = list(Product.objects.filter(main_image='') | Product.objects.filter(main_image__isnull=True))
        self.stdout.write(f'Found {len(set(existing_products.values()))} products in database with images')
        self.stdout.write(f'Found {len(empty_products)} products in database WITHOUT images')

        # Update empty products with S3 files, using normalized paths
        updated_count = 0
        processed = set()
        for s3_key in list(normalized_s3_files):
            if empty_products and s3_key not in processed:
                prod = empty_products.pop(0)
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'Would update Product ID {prod.id}: {s3_key}'))
                else:
                    prod.main_image = s3_key
                    prod.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated Product ID {prod.id}: {s3_key}'))
                updated_count += 1
                processed.add(s3_key)
                # Update the existence dict
                existing_products[s3_key] = prod
                existing_products[f'media/{s3_key}'] = prod

        # Normalize existing products that already have images but with double prefixes
        for prod in Product.objects.filter(main_image__isnull=False).exclude(main_image=''):
            if prod.main_image:
                old_path = str(prod.main_image.name)
                normalized = self._normalize_s3_key(old_path)
                if old_path != normalized and normalized in normalized_s3_files:
                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'Would normalize Product ID {prod.id}: {old_path} -> {normalized}'))
                    else:
                        prod.main_image.name = normalized
                        prod.save(update_fields=['main_image'])
                        self.stdout.write(self.style.SUCCESS(f'Normalized Product ID {prod.id}: {normalized}'))

        # Create missing database records for remaining S3 files
        created_count = 0
        for s3_key in normalized_s3_files:
            if s3_key not in processed:
                # Check multiple formats to see if it exists
                exists = (s3_key in existing_products or 
                         f'media/{s3_key}' in existing_products)
                
                if not exists:
                    # Final check: query database directly
                    try:
                        Product.objects.get(main_image=s3_key)
                        self.stdout.write(self.style.WARNING(f'Product already exists for: {s3_key}'))
                        created_count += 0
                        continue
                    except Product.DoesNotExist:
                        pass
                    
                    filename = s3_key.split('/')[-1]
                    base_name = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ')
                    product_name = f'Product {base_name}'.strip().title() or 'Product'

                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'Would create product for: {s3_key}'))
                    else:
                        try:
                            product = Product.objects.create(
                                main_image=s3_key,
                                name=product_name,
                                description='',
                                short_description='',
                                price=Decimal('1.00'),
                                compare_at_price=None,
                                category='other',
                                tags=[],
                                gallery=[],
                                stock=0,
                                sku=None,
                                dimensions='',
                                material='',
                                color='',
                                weight='',
                                featured=False,
                                is_active=False,
                                on_sale=False,
                                meta_title='',
                                meta_description='',
                            )
                            self.stdout.write(self.style.SUCCESS(f'Created product for: {s3_key}'))
                            created_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Failed to create product for {s3_key}: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Product already exists for: {s3_key}'))

        # Clean up database records for missing S3 files
        removed_count = 0
        if clean:
            for db_record in Product.objects.all():
                if db_record.main_image:
                    found = False
                    db_path = str(db_record.main_image.name)
                    db_normalized = self._normalize_s3_key(db_path)
                    for s3_key in normalized_s3_files:
                        if db_path == s3_key or db_normalized == s3_key:
                            found = True
                            break
                    if not found:
                        if dry_run:
                            self.stdout.write(self.style.WARNING(f'Would remove product image: {db_path} (ID: {db_record.id})'))
                        else:
                            db_record.delete()
                            self.stdout.write(self.style.ERROR(f'Removed product: {db_path} (ID: {db_record.id})'))
                        removed_count += 1

        self.stdout.write(f'\nProduct Summary: Updated {updated_count}, Created {created_count}, Removed {removed_count}')

    @staticmethod
    def _normalize_s3_key(key: str) -> str:
        """Remove leading 'media/' to avoid double prefix when storage adds location."""
        if not key:
            return key
        key = str(key)
        if key.startswith('media/'):
            return key[len('media/'):]
        return key
