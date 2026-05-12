"""Example Product cleanup signal registration.

The production cleanup system is registered centrally by
apps.core.apps.CoreConfig. This module is kept as a manual example for
projects that want per-app registration instead.
"""

from django.db.models.signals import pre_delete, pre_save

from apps.core.s3_cleanup import cleanup_model_files_on_delete, cleanup_replaced_files_on_save
from .models import Product


def register_product_cleanup_signals() -> None:
    """Manually register Product cleanup signals."""
    pre_delete.connect(
        cleanup_model_files_on_delete,
        sender=Product,
        weak=False,
        dispatch_uid="products.product.pre_delete.cleanup",
    )
    pre_save.connect(
        cleanup_replaced_files_on_save,
        sender=Product,
        weak=False,
        dispatch_uid="products.product.pre_save.cleanup",
    )
