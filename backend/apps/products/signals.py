from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Product


def _delete_field_file(field):
    try:
        if field and getattr(field, 'name', None):
            storage = field.storage
            name = field.name
            field.delete(save=False)
            if storage.exists(name):
                storage.delete(name)
    except Exception:
        pass


@receiver(post_delete, sender=Product)
def delete_product_main_image_on_delete(sender, instance, **kwargs):
    _delete_field_file(instance.main_image)


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
        _delete_field_file(old_file)
