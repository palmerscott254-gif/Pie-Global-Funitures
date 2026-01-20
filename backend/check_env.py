#!/usr/bin/env python
"""
Quick S3 credential verification script
Run on production to check if env vars are set
"""
import os

print("\n🔍 Checking AWS Credentials in Environment...\n")

creds = {
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_STORAGE_BUCKET_NAME': os.getenv('AWS_STORAGE_BUCKET_NAME'),
    'USE_S3': os.getenv('USE_S3'),
    'DJANGO_DEBUG': os.getenv('DJANGO_DEBUG'),
}

for key, value in creds.items():
    status = '✅' if value else '❌'
    display = value if key not in ['AWS_SECRET_ACCESS_KEY'] else '***hidden***' if value else 'NOT SET'
    print(f"{status} {key}: {display}")

# Check if ready for S3
use_s3 = (creds['USE_S3'] or '').lower() in ['true', '1', 'yes']
has_creds = all([creds['AWS_ACCESS_KEY_ID'], creds['AWS_SECRET_ACCESS_KEY'], creds['AWS_STORAGE_BUCKET_NAME']])

if has_creds and use_s3:
    print("\n✅ Ready for S3 uploads!\n")
else:
    print("\n❌ Missing credentials for S3.\n")
    print("Add these to Render Environment Variables:")
    print("  AWS_ACCESS_KEY_ID")
    print("  AWS_SECRET_ACCESS_KEY")
    print("  AWS_STORAGE_BUCKET_NAME")
    print("  USE_S3=true")
    print()
