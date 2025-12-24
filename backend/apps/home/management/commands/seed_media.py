import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.home.models import HomeVideo, SliderImage
from apps.products.models import Product

VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.ogg', '.ogv'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.svg'}

class Command(BaseCommand):
    help = "Seed DB entries for HomeVideo, SliderImage, and backfill Product.main_image from existing media files."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show actions without writing to DB')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of products to backfill')
        parser.add_argument('--assign-any', action='store_true', help='Assign any available image when no filename match is found')

    def handle(self, *args, **options):
        dry = options.get('dry_run', False)
        limit = options.get('limit', 0)
        assign_any = bool(options.get('assign_any', False))

        media_root = Path(settings.MEDIA_ROOT)
        videos_dir = media_root / 'home' / 'videos'
        sliders_dir = media_root / 'home' / 'sliders'
        products_main_dir = media_root / 'products' / 'main'

        self.stdout.write(self.style.NOTICE(f"MEDIA_ROOT: {media_root}"))

        # 1) Seed HomeVideo from files in home/videos
        created_videos = 0
        if videos_dir.exists():
            for p in sorted(videos_dir.iterdir()):
                if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
                    rel = f"home/videos/{p.name}"
                    exists = HomeVideo.objects.filter(video=rel).exists()
                    if exists:
                        self.stdout.write(self.style.WARNING(f"HomeVideo exists: {rel}"))
                        continue
                    self.stdout.write(self.style.SUCCESS(f"Create HomeVideo: {rel}"))
                    if not dry:
                        HomeVideo.objects.create(title=p.stem, video=rel, active=True)
                        created_videos += 1
        else:
            self.stdout.write(self.style.WARNING(f"Missing directory: {videos_dir}"))

        # 2) Seed SliderImage from files in home/sliders
        created_sliders = 0
        if sliders_dir.exists():
            order_counter = (SliderImage.objects.count() or 0)
            for p in sorted(sliders_dir.iterdir()):
                if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                    rel = f"home/sliders/{p.name}"
                    exists = SliderImage.objects.filter(image=rel).exists()
                    if exists:
                        self.stdout.write(self.style.WARNING(f"SliderImage exists: {rel}"))
                        continue
                    order_counter += 1
                    self.stdout.write(self.style.SUCCESS(f"Create SliderImage: {rel} (order {order_counter})"))
                    if not dry:
                        SliderImage.objects.create(title=p.stem, image=rel, order=order_counter, active=True)
                        created_sliders += 1
        else:
            self.stdout.write(self.style.WARNING(f"Missing directory: {sliders_dir}"))

        # 3) Backfill Product.main_image by filename heuristics
        #    Try to match products missing main_image with files in products/main
        created_product_images = 0
        unmatched_files = []
        if products_main_dir.exists():
            files = [p for p in products_main_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
            # Build quick lookup by normalized filename
            filename_tokens = {
                p: set(p.stem.lower().replace('-', ' ').replace('_', ' ').split())
                for p in files
            }
            used_files = set()

            products_qs = Product.objects.filter(is_active=True)
            products_qs = products_qs.order_by('-created_at')
            to_process = products_qs.filter(main_image='') | products_qs.filter(main_image__isnull=True)
            processed_count = 0

            for product in to_process:
                if limit and processed_count >= limit:
                    break
                pname_tokens = set(product.name.lower().replace('-', ' ').replace('_', ' ').split())
                pslug_tokens = set((product.slug or '').lower().replace('-', ' ').split())
                tokens = pname_tokens | pslug_tokens

                best_match = None
                best_score = 0
                for f, ftokens in filename_tokens.items():
                    score = len(tokens & ftokens)
                    if score > best_score:
                        best_score = score
                        best_match = f

                if best_match and best_score > 0:
                    rel = f"products/main/{best_match.name}"
                    self.stdout.write(self.style.SUCCESS(f"Assign main_image for product #{product.id} '{product.name}': {rel} (score {best_score})"))
                    if not dry:
                        product.main_image = rel
                        product.save(update_fields=['main_image'])
                        created_product_images += 1
                        used_files.add(best_match)
                    processed_count += 1
                else:
                    if assign_any:
                        # Pick the first unused file as a fallback
                        fallback = None
                        for f in files:
                            if f not in used_files:
                                fallback = f
                                break
                        if fallback:
                            rel = f"products/main/{fallback.name}"
                            self.stdout.write(self.style.SUCCESS(f"Fallback assign main_image for product #{product.id} '{product.name}': {rel}"))
                            if not dry:
                                product.main_image = rel
                                product.save(update_fields=['main_image'])
                                created_product_images += 1
                                used_files.add(fallback)
                            processed_count += 1
                        else:
                            unmatched_files.append(product.name)
                    else:
                        unmatched_files.append(product.name)
        else:
            self.stdout.write(self.style.WARNING(f"Missing directory: {products_main_dir}"))

        # Summary
        self.stdout.write("\n" + self.style.SUCCESS("Seeding summary:"))
        self.stdout.write(self.style.SUCCESS(f"  HomeVideo created: {created_videos}"))
        self.stdout.write(self.style.SUCCESS(f"  SliderImage created: {created_sliders}"))
        self.stdout.write(self.style.SUCCESS(f"  Product main_image backfilled: {created_product_images}"))
        if unmatched_files:
            self.stdout.write(self.style.WARNING(f"  Products without match: {len(unmatched_files)}"))
            for name in unmatched_files[:10]:
                self.stdout.write(self.style.WARNING(f"    - {name}"))
        if dry:
            self.stdout.write(self.style.NOTICE("(dry-run) No changes were written to the database."))
