"""
Django management command to verify S3 storage connectivity and configuration
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import boto3


class Command(BaseCommand):
    help = 'Verify S3 storage configuration and connectivity for media uploads'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('\n🔍 Checking S3 Storage Configuration...\n'))
        
        # Check if S3 is enabled
        if not settings.USE_S3:
            self.stdout.write(self.style.WARNING('⚠️  USE_S3 is disabled in settings'))
            return
        
        # Check credentials
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            self.stdout.write(self.style.ERROR('❌ AWS credentials are missing'))
            return
        
        self.stdout.write(self.style.SUCCESS('✅ USE_S3 is enabled'))
        self.stdout.write(f'   Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
        self.stdout.write(f'   Region: {settings.AWS_S3_REGION_NAME}')
        self.stdout.write(f'   Domain: {settings.AWS_S3_CUSTOM_DOMAIN}')
        self.stdout.write(f'   Storage: {default_storage.__class__.__name__}')
        
        # Test S3 connection
        self.stdout.write('\n🧪 Testing S3 connectivity...')
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            
            # Try to list bucket
            s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            self.stdout.write(self.style.SUCCESS('✅ S3 bucket is accessible'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Cannot access S3 bucket: {str(e)}'))
            return
        
        # Test upload capability
        self.stdout.write('\n📤 Testing file upload...')
        
        try:
            test_file_name = 'test-upload-connectivity.txt'
            test_content = 'Pie Global Furniture - S3 Upload Test'
            
            # Upload test file
            path = default_storage.save(
                f'media/{test_file_name}',
                ContentFile(test_content.encode())
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Test file uploaded: {path}'))
            
            # Get file URL
            file_url = default_storage.url(path)
            self.stdout.write(f'   URL: {file_url}')
            
            # Clean up test file
            default_storage.delete(path)
            self.stdout.write(self.style.SUCCESS('✅ Test file cleaned up'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Upload test failed: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n✅ All S3 checks passed! Admin uploads will go to S3.\n'))
