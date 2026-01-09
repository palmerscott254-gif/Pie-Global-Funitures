import boto3
from botocore.config import Config
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'List files in S3 bucket (for debugging)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefix',
            type=str,
            default='home/',
            help='S3 prefix to list (default: home/)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of files to show (default: 50)'
        )

    def handle(self, *args, **options):
        prefix = options['prefix']
        limit = options['limit']

        # Initialize S3 client
        try:
            access_key = str(settings.AWS_ACCESS_KEY_ID).strip()
            secret_key = str(settings.AWS_SECRET_ACCESS_KEY).strip()
            bucket_name = str(settings.AWS_STORAGE_BUCKET_NAME).strip()
            region = str(settings.AWS_S3_REGION_NAME).strip()
            
            if not access_key or not secret_key:
                self.stdout.write(self.style.ERROR('AWS credentials not configured'))
                return
            
            s3_config = Config(signature_version='s3v4', s3={'addressing_style': 'virtual'})
            s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
                config=s3_config,
            )
            
            self.stdout.write(f'Listing files in s3://{bucket_name}/{prefix}')
            self.stdout.write('='*70)
            
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            if 'Contents' not in response:
                self.stdout.write(self.style.WARNING(f'No files found with prefix "{prefix}"'))
                return
            
            files = [obj for obj in response['Contents'] if not obj['Key'].endswith('/')]
            self.stdout.write(f'Found {len(files)} files:\n')
            
            for idx, obj in enumerate(files, 1):
                key = obj['Key']
                size_kb = obj['Size'] / 1024
                modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f'{idx:3d}. {key}')
                self.stdout.write(f'     Size: {size_kb:.2f} KB | Modified: {modified}')
            
            if response.get('IsTruncated'):
                self.stdout.write(self.style.WARNING(f'\n... more files exist (showing first {limit})'))
            
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS(f'Total: {len(files)} files'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
