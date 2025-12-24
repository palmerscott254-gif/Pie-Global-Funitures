import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    """
    Copy bundled media files from the application image (BASE_DIR/media)
    to the production persistent disk (settings.MEDIA_ROOT, e.g., /media on Render).

    - Safe to run multiple times: skips files that already exist with same name.
    - Preserves directory structure under media/.
    - Designed for production bootstrapping of initial assets.
    """

    help = "Sync repository media directory into persistent MEDIA_ROOT (e.g., /media)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show actions without writing to disk')
        parser.add_argument('--subdir', type=str, default='', help='Optional subdir under media to sync (e.g., home/videos)')

    def handle(self, *args, **options):
        dry = options.get('dry_run', False)
        subdir = options.get('subdir', '').strip('/\\')

        base_media = Path(settings.BASE_DIR) / 'media'
        dest_media = Path(settings.MEDIA_ROOT)

        # If a subdir is provided, narrow source path
        source_root = base_media / subdir if subdir else base_media
        dest_root = dest_media / subdir if subdir else dest_media

        self.stdout.write(self.style.NOTICE(f"Source: {source_root}"))
        self.stdout.write(self.style.NOTICE(f"Destination: {dest_root}"))

        if not source_root.exists():
            self.stdout.write(self.style.WARNING(f"Source path does not exist: {source_root}"))
            return

        # Create destination root
        try:
            if not dry:
                dest_root.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create destination root: {dest_root} -> {e}"))
            return

        copied = 0
        skipped = 0

        for root, dirs, files in os.walk(source_root):
            rel_root = Path(root).relative_to(source_root)
            target_dir = dest_root / rel_root
            if not dry:
                target_dir.mkdir(parents=True, exist_ok=True)

            for fname in files:
                src = Path(root) / fname
                dst = target_dir / fname

                # Skip if file already exists (basic check by name)
                if dst.exists():
                    skipped += 1
                    self.stdout.write(self.style.WARNING(f"Skip existing: {dst}"))
                    continue

                self.stdout.write(self.style.SUCCESS(f"Copy: {src} -> {dst}"))
                if not dry:
                    try:
                        shutil.copy2(src, dst)
                        copied += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed copy: {src} -> {dst}: {e}"))

        self.stdout.write("\n" + self.style.SUCCESS("Sync summary:"))
        self.stdout.write(self.style.SUCCESS(f"  Copied: {copied}"))
        self.stdout.write(self.style.SUCCESS(f"  Skipped existing: {skipped}"))
        if dry:
            self.stdout.write(self.style.NOTICE("(dry-run) No files were actually copied."))
