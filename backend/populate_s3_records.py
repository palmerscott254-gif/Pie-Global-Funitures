#!/usr/bin/env python
"""
Quick script to populate database with S3 file records.
Run this on Render Shell after adding AWS credentials.

Usage:
    python populate_s3_records.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
django.setup()

from apps.home.models import SliderImage, HomeVideo

# Slider images that exist in S3
slider_images = [
    'home/sliders/IMG-20251218-WA0000.jpg',
    'home/sliders/IMG-20251218-WA0002.jpg',
    'home/sliders/IMG-20251218-WA0004.jpg',
    'home/sliders/IMG-20251218-WA0005.jpg',
    'home/sliders/IMG-20251218-WA0008.jpg',
    'home/sliders/IMG-20251218-WA0010.jpg',
    'home/sliders/IMG-20251218-WA0011.jpg',
    'home/sliders/IMG-20251218-WA0012.jpg',
]

# Home videos that exist in S3
home_videos = [
    'home/videos/tiktokio.com1767611179_NeHl16RLpA6Tfj18nGFI.mp4',
]

print("Populating database with S3 file records...")
print("=" * 50)

# Add slider images
created_sliders = 0
for idx, image_path in enumerate(slider_images):
    # Check if already exists
    if SliderImage.objects.filter(image=image_path).exists():
        print(f"✓ Already exists: {image_path}")
    else:
        SliderImage.objects.create(
            title=f'Slider Image {idx + 1}',
            image=image_path,
            active=True,
            order=idx
        )
        print(f"✓ Created: {image_path}")
        created_sliders += 1

print(f"\nSlider Images: {created_sliders} created, {len(slider_images) - created_sliders} already existed")

# Add home videos
created_videos = 0
for idx, video_path in enumerate(home_videos):
    # Check if already exists
    if HomeVideo.objects.filter(video=video_path).exists():
        print(f"✓ Already exists: {video_path}")
    else:
        HomeVideo.objects.create(
            title=f'Home Video {idx + 1}',
            video=video_path,
            active=True
        )
        print(f"✓ Created: {video_path}")
        created_videos += 1

print(f"Home Videos: {created_videos} created, {len(home_videos) - created_videos} already existed")
print("=" * 50)
print(f"✓ Done! Total created: {created_sliders + created_videos} records")
