from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from apps.core.file_utils import delete_field_file
from .models import SliderImage, HomeVideo


@receiver(post_delete, sender=SliderImage)
def delete_sliderimage_file_on_delete(sender, instance, **kwargs):
    delete_field_file(instance.image)


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
        delete_field_file(old_file)


@receiver(post_delete, sender=HomeVideo)
def delete_homevideo_file_on_delete(sender, instance, **kwargs):
    delete_field_file(instance.video)


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
        delete_field_file(old_file)
