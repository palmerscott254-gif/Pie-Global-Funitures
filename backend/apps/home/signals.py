"""Example Home cleanup signal registration.

The production cleanup system is registered centrally by
apps.core.apps.CoreConfig. This module is kept as a manual example for
projects that want per-app registration instead.
"""

from django.db.models.signals import pre_delete, pre_save

from apps.core.s3_cleanup import cleanup_model_files_on_delete, cleanup_replaced_files_on_save
from .models import SliderImage, HomeVideo


def register_home_cleanup_signals() -> None:
    """Manually register Home app cleanup signals."""
    pre_delete.connect(
        cleanup_model_files_on_delete,
        sender=SliderImage,
        weak=False,
        dispatch_uid="home.sliderimage.pre_delete.cleanup",
    )
    pre_save.connect(
        cleanup_replaced_files_on_save,
        sender=SliderImage,
        weak=False,
        dispatch_uid="home.sliderimage.pre_save.cleanup",
    )
    pre_delete.connect(
        cleanup_model_files_on_delete,
        sender=HomeVideo,
        weak=False,
        dispatch_uid="home.homevideo.pre_delete.cleanup",
    )
    pre_save.connect(
        cleanup_replaced_files_on_save,
        sender=HomeVideo,
        weak=False,
        dispatch_uid="home.homevideo.pre_save.cleanup",
    )
