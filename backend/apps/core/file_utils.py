"""Shared file cleanup helpers for Django media file deletion.

This module provides safe helpers for deleting FileField and ImageField
content from the configured storage backend.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def delete_field_file(field) -> bool:
    """Delete a Django file field safely.

    Uses the field's configured storage backend, so it works with AWS S3
    via django-storages as well as local filesystem storage.

    The function never raises on missing files; it logs and returns a status
    instead so admin actions do not break.
    """
    try:
        if not field or not getattr(field, "name", None):
            logger.debug("Skipped file deletion because the field was empty.")
            return False

        storage = getattr(field, "storage", None)
        name = field.name

        if storage is None:
            logger.warning("Skipped file deletion because no storage backend was available for %s.", name)
            return False

        if not storage.exists(name):
            logger.info("Skipped file deletion because it was already missing: %s", name)
            return True

        storage.delete(name)
        logger.info("Deleted file from storage: %s", name)
        return True
    except Exception:
        logger.warning("Failed to delete file from storage.", exc_info=True)
        return False


def get_file_name(field) -> Optional[str]:
    """Return a field file name safely.

    This is useful when comparing old and new file values before deciding
    whether the old file should be removed from storage.
    """
    try:
        if field and getattr(field, "name", None):
            return field.name
    except Exception:
        logger.warning("Failed to read file name from field.", exc_info=True)
    return None
