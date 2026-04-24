from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from apps.core.file_utils import delete_field_file
from .models import Product


@receiver(post_delete, sender=Product)
def delete_product_main_image_on_delete(sender, instance, **kwargs):
    delete_field_file(instance.main_image)


@receiver(pre_save, sender=Product)
def delete_product_old_main_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return
    old_file = getattr(old, 'main_image', None)
    new_file = getattr(instance, 'main_image', None)
    if old_file and new_file and old_file.name != new_file.name:
        delete_field_file(old_file)
