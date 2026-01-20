#!/usr/bin/env python
"""
Export current SliderImage and HomeVideo records to media_records.json
Run this after you finalize changes in Django Admin
This ensures the JSON only contains what you actually want
"""
import os
import json
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
django.setup()

from apps.home.models import SliderImage, HomeVideo
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import datetime

# Get current records
sliders = SliderImage.objects.all().values('id', 'title', 'image', 'order', 'active', 'uploaded_at')
videos = HomeVideo.objects.all().values('id', 'title', 'video', 'active', 'uploaded_at')

# Convert to list and format dates
sliders_list = list(sliders)
videos_list = list(videos)

# Convert datetime objects to strings
for item in sliders_list:
    if item['uploaded_at']:
        item['uploaded_at'] = str(item['uploaded_at'])

for item in videos_list:
    if item['uploaded_at']:
        item['uploaded_at'] = str(item['uploaded_at'])

# Create export structure
export_data = {
    'sliders': sliders_list,
    'videos': videos_list,
}

# Write to file
output_file = Path('media_records.json')
with open(output_file, 'w') as f:
    json.dump(export_data, f, indent=2)

print(f"✅ Exported {len(sliders_list)} slider images")
print(f"✅ Exported {len(videos_list)} videos")
print(f"📁 Saved to: {output_file}")
print("\n✨ media_records.json is now up-to-date with current database state")
print("Next: Commit and push to trigger rebuild")
