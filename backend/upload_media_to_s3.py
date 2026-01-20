#!/usr/bin/env python
"""
Upload slider images, product images, and hero videos to S3 bucket.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
django.setup()

from django.conf import settings
import boto3

def upload_to_s3():
    """Upload slider images, product images, and hero videos to S3."""
    
    # Check if S3 is configured
    if not settings.USE_S3:
        print("❌ Error: S3 is not enabled. Set USE_S3=True in .env")
        return False
    
    media_root = Path(settings.MEDIA_ROOT)
    
    if not media_root.exists():
        print(f"❌ Error: Media directory does not exist: {media_root}")
        return False
    
    # Get S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    uploaded_count = 0
    skipped_count = 0
    failed_count = 0
    
    # Define what to upload
    upload_patterns = [
        ('home/sliders', ['jpg', 'jpeg', 'png', 'webp']),  # Slider images
        ('home/videos', ['mp4', 'webm', 'mov']),  # Hero videos
        ('products/main', ['jpg', 'jpeg', 'png', 'webp']),  # Product main images
    ]
    
    print(f"\n🚀 Uploading to S3 bucket: {bucket_name}")
    print(f"📁 Source: {media_root}\n")
    
    # Upload each pattern
    for pattern_dir, extensions in upload_patterns:
        dir_path = media_root / pattern_dir
        
        if not dir_path.exists():
            print(f"⏭️  SKIP: Directory not found: {pattern_dir}")
            continue
        
        print(f"\n📂 Processing: {pattern_dir}/")
        
        for file in dir_path.iterdir():
            if not file.is_file():
                continue
            
            # Check extension
            if file.suffix.lower().lstrip('.') not in extensions:
                continue
            
            try:
                # Calculate S3 key
                relative_path = file.relative_to(media_root)
                s3_key = f"media/{relative_path}".replace('\\', '/')
                
                # Check if already exists
                try:
                    s3_client.head_object(Bucket=bucket_name, Key=s3_key)
                    print(f"  ⏭️  SKIP: {file.name}")
                    skipped_count += 1
                    continue
                except:
                    pass
                
                # Upload
                content_type = 'application/octet-stream'
                if file.suffix.lower() in ['.jpg', '.jpeg']:
                    content_type = 'image/jpeg'
                elif file.suffix.lower() == '.png':
                    content_type = 'image/png'
                elif file.suffix.lower() == '.webp':
                    content_type = 'image/webp'
                elif file.suffix.lower() == '.mp4':
                    content_type = 'video/mp4'
                elif file.suffix.lower() == '.webm':
                    content_type = 'video/webm'
                elif file.suffix.lower() == '.mov':
                    content_type = 'video/quicktime'
                
                with open(file, 'rb') as f:
                    s3_client.upload_fileobj(
                        f,
                        bucket_name,
                        s3_key,
                        ExtraArgs={
                            'ContentType': content_type,
                            'CacheControl': 'public, max-age=604800',
                        }
                    )
                
                print(f"  ✅ {file.name}")
                uploaded_count += 1
                
            except Exception as e:
                print(f"  ❌ {file.name} - {str(e)}")
                failed_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Upload Complete:")
    print(f"   ✅ Uploaded: {uploaded_count}")
    print(f"   ⏭️  Skipped: {skipped_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"{'='*60}\n")
    
    return failed_count == 0

if __name__ == '__main__':
    success = upload_to_s3()
    sys.exit(0 if success else 1)

