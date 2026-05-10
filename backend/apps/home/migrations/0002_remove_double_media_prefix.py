from django.db import migrations


def fix_media_paths_forward(apps, schema_editor):
    """Remove extra /media/ prefix from stored file paths."""
    SliderImage = apps.get_model('home', 'SliderImage')
    HomeVideo = apps.get_model('home', 'HomeVideo')
    
    # Fix SliderImage paths
    for item in SliderImage.objects.filter(image__icontains='media/home/'):
        if item.image.name.startswith('media/home/'):
            # Remove the extra 'media/' prefix
            new_name = item.image.name.replace('media/home/', 'home/', 1)
            item.image.name = new_name
            item.save(update_fields=['image'])
    
    # Fix HomeVideo paths
    for item in HomeVideo.objects.filter(video__icontains='media/home/'):
        if item.video.name.startswith('media/home/'):
            # Remove the extra 'media/' prefix
            new_name = item.video.name.replace('media/home/', 'home/', 1)
            item.video.name = new_name
            item.save(update_fields=['video'])


def fix_media_paths_reverse(apps, schema_editor):
    """Reverse: Add back the /media/ prefix."""
    SliderImage = apps.get_model('home', 'SliderImage')
    HomeVideo = apps.get_model('home', 'HomeVideo')
    
    # This is best-effort only; reverse migrations for path changes are risky
    # Only undo if the path doesn't already have the double prefix
    for item in SliderImage.objects.filter(image__icontains='home/'):
        if not item.image.name.startswith('media/') and item.image.name.startswith('home/'):
            new_name = 'media/' + item.image.name
            item.image.name = new_name
            item.save(update_fields=['image'])
    
    for item in HomeVideo.objects.filter(video__icontains='home/'):
        if not item.video.name.startswith('media/') and item.video.name.startswith('home/'):
            new_name = 'media/' + item.video.name
            item.video.name = new_name
            item.save(update_fields=['video'])


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_media_paths_forward, fix_media_paths_reverse),
    ]
