import shutil
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fix misplaced media files: move from media/media/* to media/* structure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be moved without making changes.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        media_root = Path(settings.MEDIA_ROOT)
        
        # Find all files in media/media/
        double_media_dir = media_root / "media"
        if not double_media_dir.exists():
            self.stdout.write(self.style.SUCCESS("No media/media/ directory found - nothing to fix."))
            return
        
        moved_count = 0
        for source_file in double_media_dir.rglob("*"):
            if not source_file.is_file():
                continue
            
            # Calculate relative path from double_media_dir
            rel_path = source_file.relative_to(double_media_dir)
            # Target: media/rel_path (not media/media/rel_path)
            target_file = media_root / rel_path
            
            # Create target directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            if dry_run:
                self.stdout.write(f"Would move: {source_file} → {target_file}")
            else:
                try:
                    shutil.move(str(source_file), str(target_file))
                    self.stdout.write(self.style.SUCCESS(f"✓ Moved: {rel_path}"))
                    moved_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Failed to move {source_file}: {e}"))
        
        # Clean up empty media/media directories
        try:
            if double_media_dir.exists() and not any(double_media_dir.iterdir()):
                if not dry_run:
                    double_media_dir.rmdir()
                self.stdout.write(self.style.SUCCESS("Cleaned up empty media/media/ directory"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not remove empty media/media/ dir: {e}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDry run: would move ~{moved_count} files"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Media file fix complete. Moved {moved_count} files."))
