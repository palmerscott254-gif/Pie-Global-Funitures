from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import SliderImage, HomeVideo


def _delete_field_file(field):
    try:
        if field and getattr(field, 'name', None):
            storage = field.storage
            name = field.name
            # Use FieldFile.delete which handles storage
            field.delete(save=False)
            # Double check removal if storage still has it
            if storage.exists(name):
                storage.delete(name)
    except Exception:
        # Fail-safe: never break request lifecycle due to cleanup
        pass


@receiver(post_delete, sender=SliderImage)
def delete_sliderimage_file_on_delete(sender, instance, **kwargs):
    _delete_field_file(instance.image)


@receiver(pre_save, sender=SliderImage)
def delete_sliderimage_old_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = SliderImage.objects.get(pk=instance.pk)
    except SliderImage.DoesNotExist:
        return
    old_file = getattr(old, 'image', None)
    new_file = getattr(instance, 'image', None)
    if old_file and new_file and old_file.name != new_file.name:
        _delete_field_file(old_file)


@receiver(post_delete, sender=HomeVideo)
def delete_homevideo_file_on_delete(sender, instance, **kwargs):
    _delete_field_file(instance.video)


@receiver(pre_save, sender=HomeVideo)
def delete_homevideo_old_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = HomeVideo.objects.get(pk=instance.pk)
    except HomeVideo.DoesNotExist:
        return
    old_file = getattr(old, 'video', None)
    new_file = getattr(instance, 'video', None)
    if old_file and new_file and old_file.name != new_file.name:
        _delete_field_file(old_file)
