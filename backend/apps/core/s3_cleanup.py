"""
Comprehensive AWS S3 File Cleanup System for Django Models.

This module provides reusable utilities for automatically cleaning up AWS S3 files
when Django model instances are deleted or updated. It supports both ImageField
and FileField, with proper error handling and logging.

DESIGN PRINCIPLES:
1. Reusable: Generic logic applicable to any model with file fields
2. Safe: Graceful error handling prevents crashes if files are missing
3. Logged: All operations are logged for debugging and auditing
4. Non-blocking: File deletion is synchronous but wrapped in error handling
5. Storage-agnostic: Uses Django's storage API (works with S3 and local storage)

SIGNAL PATTERN:
- pre_delete: Deletes file(s) BEFORE database record is deleted
- pre_save: Detects file changes and deletes OLD files when replaced

WHY PRE_DELETE?
- Ensures file path is available before database record is removed
- Atomic with database deletion (if S3 fails, admin sees error)
- Prevents orphaned files if transaction rolls back

WHY PRE_SAVE?
- Detects field changes before saving to database
- Allows selective deletion of only changed files
- Prevents re-deleting files if nothing changed
"""

import logging
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from django.apps import apps as django_apps
from django.db.models.fields.files import FieldFile

logger = logging.getLogger(__name__)


class S3FileCleanupManager:
    """
    Centralized manager for S3 file cleanup operations.
    
    Handles both deletion on model deletion and cleanup of replaced files.
    Provides safe, logged deletion with proper error handling.
    """
    
    def __init__(self):
        """Initialize the cleanup manager with default settings."""
        self.deleted_files: Set[str] = set()
        self.failed_deletions: List[Tuple[str, str]] = []
    
    def get_file_fields(self, model_instance: Any) -> List[str]:
        """
        Get all ImageField and FileField names from a model instance.
        
        PARAMETERS:
            model_instance: Django model instance to inspect
            
        RETURNS:
            List of field names that are ImageField or FileField
            
        EXAMPLE:
            >>> manager = S3FileCleanupManager()
            >>> product = Product.objects.first()
            >>> fields = manager.get_file_fields(product)
            >>> # Returns: ['main_image', 'gallery_image', 'video']
        """
        from django.db.models import FileField, ImageField
        
        file_fields = []
        for field in model_instance._meta.get_fields():
            # Only process ImageField and FileField instances
            if getattr(field, "concrete", False) and isinstance(field, (ImageField, FileField)):
                file_fields.append(field.name)
        
        return file_fields
    
    def get_storage(self, file_field: FieldFile) -> Any:
        """
        Get the storage backend for a file field.
        
        PARAMETERS:
            file_field: Django FieldFile object
            
        RETURNS:
            Storage backend instance (S3Boto3Storage or FileSystemStorage)
        """
        return getattr(file_field, 'storage', None)
    
    def delete_file(
        self,
        file_field: Optional[FieldFile],
        context: str = "model_deletion"
    ) -> bool:
        """
        Safely delete a single file from storage.
        
        Handles both S3 and local storage via Django's storage API.
        Does NOT crash if file is missing or storage fails.
        
        PARAMETERS:
            file_field: Django FieldFile object (e.g., instance.main_image)
            context: String describing deletion context for logging
                     ('model_deletion', 'field_replaced', 'manual_cleanup')
            
        RETURNS:
            True if deletion succeeded, False otherwise
            
        WHY SAFE:
            - Checks if field exists and has a name before attempting delete
            - Catches all exceptions to prevent admin crashes
            - Uses storage.exists() to verify before S3 deletion
            - Logs all failures for debugging
            
        EXAMPLE:
            >>> manager = S3FileCleanupManager()
            >>> product = Product.objects.first()
            >>> manager.delete_file(product.main_image, 'model_deletion')
            True
        """
        # Guard: Check if field is empty/None
        if not file_field:
            logger.debug(f"Skipping deletion: file_field is None ({context})")
            return True
        
        # Guard: Check if field has a file path
        file_name = getattr(file_field, 'name', None)
        if not file_name:
            logger.debug(f"Skipping deletion: file_field.name is empty ({context})")
            return True
        
        try:
            # Get storage backend (S3, local, etc.)
            storage = self.get_storage(file_field)
            if not storage:
                logger.warning(f"No storage backend for {file_name} ({context})")
                return False
            
            # Check if file exists in storage BEFORE attempting deletion
            # This prevents errors when file is already missing from S3
            if not storage.exists(file_name):
                logger.warning(
                    f"File not found in storage (already deleted?): {file_name} ({context})"
                )
                return True  # Not an error - file is already gone
            
            # Delete from storage backend
            # This works with both S3 (boto3) and local FileSystemStorage
            storage.delete(file_name)
            
            # Track successful deletion
            self.deleted_files.add(file_name)
            logger.info(f"Deleted file from storage: {file_name} ({context})")
            return True
            
        except Exception as e:
            # Log error but don't crash
            # This is critical - we never want admin operations to fail due to S3 issues
            self.failed_deletions.append((file_name, str(e)))
            logger.error(
                f"Failed to delete file from storage: {file_name}",
                extra={
                    'context': context,
                    'error': str(e),
                    'file_name': file_name,
                },
                exc_info=True
            )
            return False
    
    def is_file_referenced_elsewhere_after_delete(self, file_name: str, current_instance: Any) -> bool:
        """Return True if another database row still references this file.

        For pre_delete cleanup we intentionally ignore references that belong
        to the row being deleted, because the row itself will disappear.
        """
        from django.db.models import FileField, ImageField

        current_model = current_instance.__class__
        current_pk = current_instance.pk

        for model in django_apps.get_models():
            for field in model._meta.get_fields():
                if not getattr(field, "concrete", False) or not isinstance(field, (FileField, ImageField)):
                    continue

                qs = model._default_manager.filter(**{field.name: file_name})

                if model is current_model and current_pk is not None:
                    qs = qs.exclude(pk=current_pk)

                if qs.exists():
                    return True

        return False

    def is_file_referenced_elsewhere_on_update(self, file_name: str, current_instance: Any, current_field_name: str) -> bool:
        """Return True if another row or another field on the same row still uses the file."""
        from django.db.models import FileField, ImageField

        current_model = current_instance.__class__
        current_pk = current_instance.pk

        for model in django_apps.get_models():
            for field in model._meta.get_fields():
                if not getattr(field, "concrete", False) or not isinstance(field, (FileField, ImageField)):
                    continue

                qs = model._default_manager.filter(**{field.name: file_name})

                if model is current_model and field.name == current_field_name and current_pk is not None:
                    qs = qs.exclude(pk=current_pk)

                if qs.exists():
                    return True

        return False

    def cleanup_on_delete(self, instance: Any) -> Dict[str, Any]:
        """Delete all media files when a model instance is deleted."""
        model_name = instance.__class__.__name__
        instance_pk = instance.pk

        self.deleted_files.clear()
        self.failed_deletions.clear()
        file_fields = self.get_file_fields(instance)

        if not file_fields:
            logger.debug(f"{model_name}(pk={instance_pk}) has no file fields")
            return {
                'model': model_name,
                'instance_pk': instance_pk,
                'deleted_files': [],
                'failed_deletions': [],
                'total_processed': 0,
            }

        for field_name in file_fields:
            file_field = getattr(instance, field_name, None)
            file_name = getattr(file_field, 'name', None) if file_field else None
            if not file_name:
                logger.debug("Skipped deletion for empty field %s.%s", model_name, field_name)
                continue
            if self.is_file_referenced_elsewhere_after_delete(file_name, instance):
                logger.warning("Skipped deletion for shared file after delete: %s (%s.%s)", file_name, model_name, field_name)
                continue
            self.delete_file(file_field, context=f"{model_name}.{field_name}_on_delete")

        logger.info(
            f"Cleanup on delete: {model_name}(pk={instance_pk}) - "
            f"deleted {len(self.deleted_files)} files, "
            f"{len(self.failed_deletions)} failed"
        )

        return {
            'model': model_name,
            'instance_pk': instance_pk,
            'deleted_files': list(self.deleted_files),
            'failed_deletions': self.failed_deletions,
            'total_processed': len(file_fields),
        }
    
    def cleanup_replaced_files(
        self,
        old_instance: Any,
        new_instance: Any,
        fields_to_check: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Delete old files when they are replaced in a model update.
        
        Called via pre_save signal. Compares old and new field values,
        deleting files that were replaced but keeping files that weren't changed.
        
        PARAMETERS:
            old_instance: Original model instance from database
            new_instance: New model instance being saved
            fields_to_check: Specific file fields to check (default: all)
            
        RETURNS:
            Dictionary with cleanup statistics:
            {
                'model': 'Product',
                'instance_pk': 123,
                'replaced_files': {
                    'main_image': 'products/main/old.jpg'
                },
                'unchanged_files': ['...'],
                'total_checked': 3,
            }
            
        WHY IMPORTANT:
            - Admin users expect that uploading a new image removes the old one
            - Prevents S3 bucket bloat from multiple versions of same field
            - Tracks which files were intentionally replaced vs. unchanged
            
        EXAMPLE:
            >>> manager = S3FileCleanupManager()
            >>> old_product = Product.objects.get(pk=123)
            >>> new_product = old_product  # After editing in admin
            >>> new_product.main_image = new_file
            >>> stats = manager.cleanup_replaced_files(old_product, new_product)
            >>> print(stats['replaced_files'])
            {'main_image': 'products/main/old.jpg'}
        """
        model_name = old_instance.__class__.__name__
        instance_pk = old_instance.pk
        
        # Reset tracking for this operation
        self.deleted_files.clear()
        self.failed_deletions.clear()
        
        # Determine which fields to check
        if fields_to_check is None:
            fields_to_check = self.get_file_fields(old_instance)
        
        replaced_files = {}
        unchanged_files = []
        
        for field_name in fields_to_check:
            old_field = getattr(old_instance, field_name, None)
            new_field = getattr(new_instance, field_name, None)

            old_name = getattr(old_field, 'name', None) if old_field else None
            new_name = getattr(new_field, 'name', None) if new_field else None

            # Case 1: Field was cleared (old file exists, new is empty)
            if old_name and not new_name:
                if self.is_file_referenced_elsewhere_on_update(old_name, old_instance, field_name):
                    logger.warning("Skipped deletion for shared file on update: %s (%s.%s)", old_name, model_name, field_name)
                else:
                    self.delete_file(old_field, context=f"{model_name}.{field_name}_cleared")
                replaced_files[field_name] = old_name
                logger.info(
                    f"File field cleared: {model_name}.{field_name}",
                    extra={'old_file': old_name}
                )

            # Case 2: Field was replaced (both exist and differ)
            elif old_name and new_name and old_name != new_name:
                if self.is_file_referenced_elsewhere_on_update(old_name, old_instance, field_name):
                    logger.warning("Skipped deletion for shared file on update: %s (%s.%s)", old_name, model_name, field_name)
                else:
                    self.delete_file(old_field, context=f"{model_name}.{field_name}_replaced")
                replaced_files[field_name] = old_name
                logger.info(
                    f"File field replaced: {model_name}.{field_name}",
                    extra={'old_file': old_name, 'new_file': new_name}
                )

            # Case 3: Field unchanged
            else:
                unchanged_files.append(field_name)
        
        # Log summary
        logger.info(
            f"Cleanup on update: {model_name}(pk={instance_pk}) - "
            f"replaced {len(replaced_files)} files"
        )
        
        return {
            'model': model_name,
            'instance_pk': instance_pk,
            'replaced_files': replaced_files,
            'unchanged_files': unchanged_files,
            'total_checked': len(fields_to_check),
        }


# Global manager instance
# This is a singleton used by all signal handlers
cleanup_manager = S3FileCleanupManager()


def cleanup_model_files_on_delete(sender: Any, instance: Any, **kwargs) -> None:
    """
    Signal handler for pre_delete event.
    
    Automatically called when a model instance is deleted from admin or code.
    Deletes all associated media files from S3.
    
    SIGNAL: pre_delete
    WHY PRE_DELETE:
        - File path exists in instance before database deletion
        - Atomic with database transaction
        - If S3 fails, admin sees error immediately
    
    PARAMETERS:
        sender: Model class being deleted (Product, SliderImage, etc.)
        instance: Instance of model being deleted
        **kwargs: Additional signal parameters
        
    USAGE (in your app's signals.py):
        from django.db.models.signals import pre_delete
        from django.dispatch import receiver
        from apps.core.s3_cleanup import cleanup_model_files_on_delete
        from .models import YourModel
        
        @receiver(pre_delete, sender=YourModel)
        def handle_yourmodel_delete(sender, instance, **kwargs):
            cleanup_model_files_on_delete(sender, instance, **kwargs)
    
    ALTERNATIVE (no decorator needed):
        # In apps.py:
        def ready(self):
            from django.db.models.signals import pre_delete
            from apps.core.s3_cleanup import cleanup_model_files_on_delete
            pre_delete.connect(cleanup_model_files_on_delete, sender=YourModel)
    """
    try:
        stats = cleanup_manager.cleanup_on_delete(instance)
        logger.info(f"Cleanup stats: {stats}")
    except Exception as e:
        # Critical: Never crash the admin due to cleanup failures
        logger.error(
            f"Fatal error during file cleanup for {sender.__name__}",
            exc_info=True
        )


def cleanup_replaced_files_on_save(sender: Any, instance: Any, **kwargs) -> None:
    """
    Signal handler for pre_save event.
    
    Automatically called before a model instance is saved to database.
    Detects if file fields changed and deletes old files from S3.
    
    SIGNAL: pre_save
    WHY PRE_SAVE:
        - Compares old vs. new before database commit
        - Prevents deleting unchanged files
        - Allows tracking which files were intentionally replaced
    
    PARAMETERS:
        sender: Model class being saved (Product, SliderImage, etc.)
        instance: Instance of model being saved
        **kwargs: Additional signal parameters
        
    USAGE (in your app's signals.py):
        from django.db.models.signals import pre_save
        from django.dispatch import receiver
        from apps.core.s3_cleanup import cleanup_replaced_files_on_save
        from .models import YourModel
        
        @receiver(pre_save, sender=YourModel)
        def handle_yourmodel_save(sender, instance, **kwargs):
            cleanup_replaced_files_on_save(sender, instance, **kwargs)
    
    IMPORTANT NOTE:
        This only works for UPDATE operations (when instance.pk exists).
        New instances (pk=None) are skipped to avoid errors.
    """
    # Only process existing instances (updates, not creates)
    if not instance.pk:
        return
    
    try:
        # Fetch old instance from database
        old_instance = sender.objects.get(pk=instance.pk)
        
        # Check for replaced files
        stats = cleanup_manager.cleanup_replaced_files(old_instance, instance)
        
        if stats['replaced_files']:
            logger.info(f"Cleanup stats: {stats}")
    
    except sender.DoesNotExist:
        # Instance doesn't exist in database yet (shouldn't happen in pre_save)
        logger.warning(f"Instance {sender.__name__}(pk={instance.pk}) not found during pre_save")
    except Exception as e:
        # Critical: Never crash the save due to cleanup failures
        logger.error(
            f"Fatal error during file cleanup on save for {sender.__name__}",
            exc_info=True
        )


# ============================================================================
# HELPER FUNCTIONS FOR COMMON PATTERNS
# ============================================================================

def register_model_cleanup(model_class: Any, fields: Optional[List[str]] = None) -> None:
    """
    Register automatic cleanup for a model with a single call.
    
    Convenience function to register both pre_delete and pre_save signals
    for a model. Simpler than manually creating signal handlers.
    
    PARAMETERS:
        model_class: Django model class to register (e.g., Product)
        fields: Optional list of specific fields to monitor (default: all)
        
    EXAMPLE:
        # In your app's apps.py ready() method:
        from django.apps import AppConfig
        from apps.core.s3_cleanup import register_model_cleanup
        
        class ProductsConfig(AppConfig):
            name = 'apps.products'
            
            def ready(self):
                from .models import Product
                register_model_cleanup(Product)
    
    WHY USE THIS:
        - No need to write separate signal handlers
        - Consistent cleanup behavior across all models
        - Single line of code per model
    """
    register_media_model_cleanup(model_class, fields=fields)


def register_media_model_cleanup(
    model_class: Any,
    fields: Optional[List[str]] = None,
) -> None:
    """Register cleanup for a model and optionally restrict update checks to specific fields."""
    from django.db.models.signals import pre_delete, pre_save

    delete_uid = f"s3-cleanup-delete-{model_class._meta.label_lower}"
    save_uid = f"s3-cleanup-save-{model_class._meta.label_lower}"

    def handle_delete(sender, instance, **kwargs):
        cleanup_model_files_on_delete(sender, instance, **kwargs)

    def handle_save(sender, instance, **kwargs):
        if not instance.pk:
            return
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            logger.warning("Instance %s(pk=%s) not found during pre_save cleanup", sender.__name__, instance.pk)
            return
        cleanup_manager.cleanup_replaced_files(old_instance, instance, fields_to_check=fields)

    pre_delete.connect(handle_delete, sender=model_class, weak=False, dispatch_uid=delete_uid)
    pre_save.connect(handle_save, sender=model_class, weak=False, dispatch_uid=save_uid)
    logger.info("Registered media cleanup signals for %s", model_class.__name__)


def register_all_media_model_cleanup(app_labels: Optional[Iterable[str]] = None) -> None:
    """Register cleanup for every installed model that has file fields.

    This is the production-safe fallback for future models: any new model with
    an ImageField or FileField will automatically be covered after startup.
    """
    allowed_labels = set(app_labels) if app_labels is not None else None

    for model in django_apps.get_models():
        if allowed_labels is not None and model._meta.app_label not in allowed_labels:
            continue
        from django.db.models import FileField, ImageField
        monitored = [
            field.name
            for field in model._meta.get_fields()
            if getattr(field, "concrete", False) and isinstance(field, (FileField, ImageField))
        ]
        if monitored:
            register_media_model_cleanup(model, fields=monitored)
